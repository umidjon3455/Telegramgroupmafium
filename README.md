# Telegramgroupmafium

Telegram guruhlari uchun Mafia o‘yini boti va uning Django asosidagi web qismi.

## Texnologiyalar

- Python 3.11
- aiogram 3
- SQLite
- Django 5
- HTML va CSS

## Telegram bot

### Imkoniyatlar

- Guruhda o‘yin xonasi yaratish va unga qo‘shilish
- Mafia, Doktor, Komissar va Aholi rollari
- Shaxsiy chat orqali tungi harakatlar
- Guruhda kunduzgi ovoz berish
- O‘yinchi profili, statistika, XP, darajalar va reyting

### O‘rnatish

Windows PowerShell orqali:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` faylida `BOT_TOKEN` qiymatini BotFather bergan token bilan almashtiring. Tokenni repozitoriyga yuklamang.

### Ishga tushirish

```powershell
python -m bot.main
```

O‘yinchilar botga shaxsiy chatda `/start` yuborishi kerak. Keyin botni guruhga qo‘shing.

### Buyruqlar

| Buyruq | Vazifasi |
|---|---|
| `/start` | Botni ishga tushirish |
| `/help` | Yordam |
| `/game` | O‘yin xonasi yaratish |
| `/join` | Xonaga qo‘shilish |
| `/leave` | Kutish xonasidan chiqish |
| `/startgame` | O‘yinni boshlash |
| `/cancelgame` | Kutish xonasini bekor qilish |
| `/profile` | Shaxsiy statistika |
| `/top` | Reyting |

## Django web qismi

Web ilova `web/` papkasida joylashgan. Hozirgi versiyada ro‘yxatdan o‘tish, kirish, o‘yinchi profili, reyting, o‘yin xonalari va Django admin mavjud. Xonada kamida 5 o‘yinchi bo‘lganda rollar taqsimlanadi.

### O‘rnatish va ishga tushirish

```powershell
cd web
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` faylini oching va `DJANGO_SECRET_KEY` hamda `TELEGRAM_SYNC_KEY` qiymatlarini o‘zgartiring. Mahalliy ishlab chiqish uchun `DJANGO_DEBUG=True` qoldirilishi mumkin.

So‘ng:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Sayt: http://127.0.0.1:8000/  
Admin: http://127.0.0.1:8000/admin/

## O‘rnatishdan keyingi tekshiruv

Bot va Django web qismi alohida virtual muhitlarda ishlatilishi tavsiya etiladi. Yuqoridagi buyruqlarni tegishli papkada bajaring.

Django papkasida quyidagi buyruqlarni ketma-ket bajaring:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
```

- `check` — Django konfiguratsiyasini tekshiradi.
- `makemigrations --check --dry-run` — model o‘zgarishlari uchun migratsiya yetishmayotganini tekshiradi, fayl yaratmaydi.
- `migrate` — ma’lumotlar bazasi jadvallarini yaratadi yoki yangilaydi.
- `test` — mavjud Django testlarini ishga tushiradi.

Bot papkasining ildizida sintaksisni tekshirish uchun:

```powershell
python -m compileall -q bot
```

Botni ishga tushirishdan oldin ildizdagi `.env` faylida haqiqiy `BOT_TOKEN` bo‘lishi shart. Django uchun esa `web/.env` ichida `DJANGO_SECRET_KEY` bo‘lishi kerak. Bu maxfiy qiymatlarni GitHub'ga yubormang.

## Hozirgi cheklovlar

- Botdagi faol o‘yin holati xotirada saqlanadi. Bot qayta ishga tushsa, davom etayotgan o‘yin tiklanmaydi.
- Django web qismida hozircha kutish xonasi va rol taqsimlash mavjud. To‘liq tungi/kunduzgi o‘yin mexanikasi hali ishlab chiqilmagan.
- Bot va sayt o‘rtasidagi statistika sinxronlash endpointi mavjud, ammo bot tomonidan yuborish integratsiyasi hali ulanmagan.
- Loyihani ommaviy serverga joylashdan oldin maxfiy kalitlar, `DEBUG`, `ALLOWED_HOSTS` va xavfsizlik sozlamalarini tekshirish, shuningdek real muhitda sinovdan o‘tkazish kerak.
