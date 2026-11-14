import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from .config import BOT_TOKEN
from .database import init_db, register_player, record_game, get_profile, get_top
from .game import MafiaGame, MIN_PLAYERS
from .keyboards import day_keyboard, night_keyboard

logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
games = {}

ROLE_NAMES = {
    "mafia": "🕵️ Mafia", "doctor": "🧑‍⚕️ Doktor",
    "detective": "🕵️ Komissar", "citizen": "👨‍🌾 Tinch aholi",
}
ACHIEVEMENTS = [
    (1, "🌱 Birinchi qadam", "Birinchi o‘yiningiz"),
    (5, "🎮 Tajribali", "5 ta o‘yinda qatnashish"),
    (10, "🏅 Faxriy o‘yinchi", "10 ta o‘yinda qatnashish"),
]

async def send_lobby(chat_id, game):
    names = "\n".join(f"• {p['name']}" for p in game.players.values()) or "Hali hech kim yo‘q"
    await bot.send_message(chat_id,
        f"🎭 <b>Mafia xonasi ochildi!</b>\n\n👥 O‘yinchilar ({len(game.players)}):\n{names}\n\n"
        "Qo‘shilish: /join\nBoshlash: /startgame", parse_mode="HTML")

async def finish_game(chat_id, game, side):
    winners = [uid for uid, p in game.players.items()
               if (p["role"] == "mafia") == (side == "mafia")]
    await record_game(game.players, winners)
    winner_text = "🕵️ Mafia jamoasi g‘alaba qozondi!" if side == "mafia" else "🏘 Tinch aholi g‘alaba qozondi!"
    details = "\n".join(
        f"{'🟢' if uid in winners else '⚪'} {p['name']} — {ROLE_NAMES[p['role']]}"
        for uid, p in game.players.items())
    await bot.send_message(chat_id, f"🏆 <b>O‘YIN TUGADI!</b>\n{winner_text}\n\n{details}", parse_mode="HTML")
    games.pop(chat_id, None)

async def start_night(chat_id, game):
    game.phase = "night"
    game.night += 1
    game.night_actions = {}
    await bot.send_message(chat_id,
        f"🌙 <b>{game.night}-kecha boshlandi.</b> Maxsus rollar shaxsiy chatdagi tugmalardan foydalanadi.",
        parse_mode="HTML")
    for uid in game.alive_ids():
        role = game.players[uid]["role"]
        if role not in ("mafia", "doctor", "detective"):
            continue
        try:
            prompt = {
                "mafia": "🌙 Mafia: kimni o‘yindan chiqarishni tanlang.",
                "doctor": "🩺 Doktor: kimni himoya qilasiz?",
                "detective": "🔎 Komissar: kimning rolini tekshirasiz?",
            }[role]
            await bot.send_message(uid, prompt, reply_markup=night_keyboard(game, role))
        except (TelegramForbiddenError, TelegramBadRequest):
            await bot.send_message(chat_id,
                f"⚠️ {game.players[uid]['name']} bot bilan shaxsiy chatni ochmagan. U botga /start yuborishi kerak.")

async def resolve_night(chat_id, game):
    required = set(game.role_ids("mafia") + game.role_ids("doctor") + game.role_ids("detective"))
    if not required.issubset(game.night_actions):
        return
    victim, _ = game.night_result()
    if victim:
        game.eliminate(victim)
        await bot.send_message(chat_id, f"🌅 Tong otdi. Kechasi {game.players[victim]['name']} o‘yindan chiqdi.")
    else:
        await bot.send_message(chat_id, "🌅 Tong otdi. Bu kecha hech kim o‘yindan chiqmadi.")
    winner = game.winner()
    if winner:
        await finish_game(chat_id, game, winner)
        return
    game.phase = "day"
    game.votes = {}
    alive = "\n".join(f"• {game.players[uid]['name']}" for uid in game.alive_ids())
    await bot.send_message(chat_id,
        f"☀️ <b>KUNDUZGI MUHOKAMA</b>\nTirik o‘yinchilar:\n{alive}\n\nOvoz berish uchun tugmani bosing.",
        reply_markup=day_keyboard(game), parse_mode="HTML")

async def resolve_day(chat_id, game):
    if len(game.votes) < len(game.alive_ids()):
        return
    out = game.day_result()
    if out:
        game.eliminate(out)
        await bot.send_message(chat_id,
            f"🗳 Ovoz berish yakunlandi. {game.players[out]['name']} o‘yindan chiqarildi. Roli: {ROLE_NAMES[game.players[out]['role']]}.")
    else:
        await bot.send_message(chat_id, "🗳 Ovozlar teng bo‘ldi. Hech kim chiqarilmadi.")
    winner = game.winner()
    if winner:
        await finish_game(chat_id, game, winner)
    else:
        await start_night(chat_id, game)

@dp.message(CommandStart())
async def start(message: Message):
    await register_player(message.from_user)
    await message.answer(
        "🎭 <b>Telegramgroupmafium</b> botiga xush kelibsiz!\n"
        "Botni shaxsiy chatda ishga tushiring, keyin guruhdagi Mafia o‘yiniga qo‘shiling.\n/help — buyruqlar",
        parse_mode="HTML")

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "🎮 <b>Mafia bot buyruqlari</b>\n/game — guruhda xona ochish\n/join — qo‘shilish\n/leave — chiqish\n"
        "/startgame — o‘yinni boshlash (xona egasi)\n/cancelgame — kutish xonasini bekor qilish\n"
        "/profile — statistika\n/top — reyting\n\nMaxfiy rollar uchun botga shaxsiy chatda /start yuboring.",
        parse_mode="HTML")

@dp.message(Command("game"))
async def create_game(message: Message):
    if message.chat.type == "private":
        await message.answer("O‘yin uchun avval botni guruhga qo‘shing.")
        return
    if message.chat.id in games:
        await message.answer("Bu guruhda allaqachon o‘yin xonasi bor.")
        return
    games[message.chat.id] = MafiaGame(message.chat.id, message.from_user.id)
    await register_player(message.from_user)
    games[message.chat.id].add_player(message.from_user)
    await send_lobby(message.chat.id, games[message.chat.id])

@dp.message(Command("join"))
async def join_game(message: Message):
    game = games.get(message.chat.id)
    if not game:
        await message.answer("Avval /game bilan xona oching.")
        return
    await register_player(message.from_user)
    ok, response = game.add_player(message.from_user)
    await message.answer(response)
    if ok:
        await send_lobby(message.chat.id, game)

@dp.message(Command("leave"))
async def leave_game(message: Message):
    game = games.get(message.chat.id)
    if not game or not game.remove_player(message.from_user.id):
        await message.answer("Hozir kutish xonasidan chiqa olmaysiz.")
        return
    await message.answer("Xonadan chiqdingiz.")
    await send_lobby(message.chat.id, game)

@dp.message(Command("cancelgame"))
async def cancel_game(message: Message):
    game = games.get(message.chat.id)
    if not game or game.host_id != message.from_user.id or game.phase != "lobby":
        await message.answer("Bu buyruqni faqat xona egasi kutish vaqtida ishlata oladi.")
        return
    games.pop(message.chat.id, None)
    await message.answer("Xona bekor qilindi.")

@dp.message(Command("startgame"))
async def start_game(message: Message):
    game = games.get(message.chat.id)
    if not game or game.phase != "lobby":
        await message.answer("Boshlash uchun avval /game yuboring.")
        return
    if game.host_id != message.from_user.id:
        await message.answer("O‘yinni faqat xona egasi boshlashi mumkin.")
        return
    if len(game.players) < MIN_PLAYERS:
        await message.answer(f"Kamida {MIN_PLAYERS} o‘yinchi kerak. Hozir: {len(game.players)}")
        return
    game.assign_roles()
    failed = []
    for uid, player in game.players.items():
        try:
            await bot.send_message(uid, f"🎭 Sizning rolingiz: <b>{ROLE_NAMES[player['role']]}</b>", parse_mode="HTML")
        except (TelegramForbiddenError, TelegramBadRequest):
            failed.append(player["name"])
    if failed:
        games.pop(message.chat.id, None)
        await message.answer("Quyidagi o‘yinchilar botga shaxsiy /start yubormagan: " + ", ".join(failed) + ". Xona bekor qilindi; hamma /start yuborgach qayta urinib ko‘ring.")
        return
    await message.answer("🎭 Rollar tarqatildi! O‘yin boshlandi.")
    await start_night(message.chat.id, game)

@dp.callback_query(F.data.startswith("dayvote:"))
async def day_vote(call: CallbackQuery):
    _, chat_id, target_id = call.data.split(":")
    game = games.get(int(chat_id))
    if not game or game.phase != "day":
        await call.answer("Ovoz berish faol emas.", show_alert=True)
        return
    uid, target = call.from_user.id, int(target_id)
    if uid not in game.alive_ids() or target not in game.alive_ids() or uid == target:
        await call.answer("Bu ovoz berish uchun ruxsat yo‘q.", show_alert=True)
        return
    game.votes[uid] = target
    await call.answer("Ovozingiz qabul qilindi.")
    await resolve_day(game.chat_id, game)

@dp.callback_query(F.data.startswith("night:"))
async def night_action(call: CallbackQuery):
    _, role, chat_id, target_id = call.data.split(":")
    target = int(target_id)
    game = games.get(int(chat_id))
    if not game or game.phase != "night":
        await call.answer("Tun bosqichi tugagan.", show_alert=True)
        return
    player = game.players.get(call.from_user.id)
    if not player or not player["alive"] or player["role"] != role:
        await call.answer("Bu harakat siz uchun mavjud emas.", show_alert=True)
        return
    if target not in game.alive_ids() or target == call.from_user.id:
        await call.answer("Bu o‘yinchini tanlab bo‘lmaydi.", show_alert=True)
        return
    game.night_actions[call.from_user.id] = target
    if role == "detective":
        target_role = game.players[target]["role"]
        await call.message.answer("🔎 Tekshiruv natijasi: bu o‘yinchi " + ("Mafia." if target_role == "mafia" else "Mafia emas."))
    await call.answer("Tanlovingiz qabul qilindi.")
    await resolve_night(game.chat_id, game)

@dp.message(Command("profile"))
async def profile(message: Message):
    row = await get_profile(message.from_user.id)
    if not row:
        await message.answer("Profil topilmadi. /start yuboring.")
        return
    games_count, wins, losses, xp = row["games"], row["wins"], row["losses"], row["xp"]
    level = xp // 100 + 1
    unlocked = [name for threshold, name, _ in ACHIEVEMENTS if games_count >= threshold]
    await message.answer(
        f"👤 <b>{row['full_name']}</b>\n🎮 O‘yinlar: {games_count}\n🏆 G‘alabalar: {wins}\n"
        f"📉 Mag‘lubiyatlar: {losses}\n⭐ XP: {xp}\n🎖 Daraja: {level}\n\n"
        f"🏅 Yutuqlar: {', '.join(unlocked) if unlocked else 'Hozircha yo‘q'}",
        parse_mode="HTML")

@dp.message(Command("top"))
async def top(message: Message):
    rows = await get_top()
    if not rows:
        await message.answer("Reyting hozircha bo‘sh.")
        return
    lines = [f"{i}. {r['full_name']} — 🏆 {r['wins']} | ⭐ {r['xp']} XP" for i, r in enumerate(rows, 1)]
    await message.answer("🏆 <b>TOP o‘yinchilar</b>\n" + "\n".join(lines), parse_mode="HTML")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
