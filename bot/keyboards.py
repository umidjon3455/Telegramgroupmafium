from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def targets_keyboard(game, prefix):
    rows = []
    for uid in game.alive_ids():
        player = game.players[uid]
        rows.append([InlineKeyboardButton(
            text=player["name"][:30],
            callback_data=f"{prefix}:{game.chat_id}:{uid}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def day_keyboard(game):
    return targets_keyboard(game, "dayvote")

def night_keyboard(game, role):
    return targets_keyboard(game, f"night:{role}")
