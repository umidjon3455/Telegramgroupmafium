# Telegramgroupmafium

Telegram guruhlari uchun Mafia o‘yini boti. Python 3.11, aiogram 3 va SQLite asosida.

## Imkoniyatlar
- Guruhda o‘yin xonasi ochish: `/game`
- Qatnashish: `/join`, chiqish: `/leave`
- Boshlash: `/startgame` (faqat xona egasi)
- Mafia, Doktor, Komissar va Aholi rollari
- Tungi harakatlar shaxsiy chatdagi tugmalar orqali
- Kunduzgi ovoz berish guruhda
- Profil, statistika, reyting, XP, darajalar va yutuqlar
- O‘yin natijalari SQLite bazasiga yoziladi

## Talablar
- Python 3.11
- Telegram bot tokeni
- Bot guruhda xabar yuborish va callback tugmalariga javob berish huquqiga ega bo‘lishi kerak.

## O‘rnatish (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` faylini ochib, `BOT_TOKEN` qiymatiga BotFather bergan tokenni kiriting. Tokenni hech qachon GitHub'ga yuklamang.

## Ishga tushirish
```powershell
python -m bot.main
```

Avval har bir o‘yinchi botga shaxsiy chatda `/start` yuborishi kerak. So‘ng botni guruhga qo‘shing.

## O‘yin tartibi
1. Guruhda `/game` yuboring.
2. O‘yinchilar `/join` bilan qo‘shiladi (kamida 5 kishi).
3. Xona egasi `/startgame` yuboradi.
4. Rollar shaxsiy chatga jo‘natiladi.
5. Kechasi maxsus rollar shaxsiy tugmalardan foydalanadi.
6. Kunduzi guruhdagi ovoz berish tugmalaridan foydalaniladi.
7. G‘olib aniqlanganda natija va statistika saqlanadi.

## Buyruqlar
- `/start` — botni ishga tushirish
- `/help` — yordam
- `/game` — guruhda xona ochish
- `/join` — o‘yinga qo‘shilish
- `/leave` — kutish xonasidan chiqish
- `/startgame` — o‘yinni boshlash
- `/cancelgame` — kutish xonasini bekor qilish
- `/profile` — shaxsiy statistika
- `/top` — reyting

## Hozirgi cheklov
Faol o‘yin holati hozircha bot xotirasida saqlanadi. Bot qayta ishga tushsa, davom etayotgan o‘yin to‘xtaydi; profil va statistika SQLite'da qoladi. Bu boshlang‘ich versiya bo‘lib, real guruhda to‘liq sinovdan o‘tkazish va keyingi takomillashtirish talab qilinadi.


## Django web platform (development)

A Django website scaffold is available in `web/`:
- Registration and login
- Player profile with games, wins, losses, XP and level
- Leaderboard
- Web game rooms, joining and role assignment (minimum 5 players)
- Django admin for profiles and rooms
- Protected endpoint `/api/telegram-sync/` for future bot-to-site statistics synchronization

### Run the website (Windows PowerShell)
```powershell
cd web
py -3.11 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Configure a strong `DJANGO_SECRET_KEY` and a private `TELEGRAM_SYNC_KEY` before deployment. The website room flow currently provides a lobby and role assignment; full web-based night/day turns and live synchronization with the Telegram bot are follow-up development tasks. Do not use the development defaults on a public server.
