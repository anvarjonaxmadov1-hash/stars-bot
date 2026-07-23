# Telegram Premium & Stars Bot (UZ/RU/EN)

Kompyutersiz, faqat telefon orqali ishga tushirish yo'riqnomasi.

## 1-qadam: Bot yaratish
1. Telegramda **@BotFather** ga yozing.
2. `/newbot` yuboring, nom va username bering.
3. Sizga **BOT_TOKEN** beriladi — saqlab qo'ying.

## 2-qadam: Admin ID'ingizni bilib olish
1. **@userinfobot** ga yozing — u sizning Telegram ID'ingizni beradi.
2. Shu raqamni saqlab qo'ying (ADMIN_IDS uchun kerak).

## 3-qadam: Kodni GitHub'ga yuklash
1. Telefon brauzerida **github.com** ga kiring, ro'yxatdan o'ting.
2. Yangi repository (masalan `stars-bot`) yarating — Public yoki Private.
3. "Upload files" tugmasi orqali shu papkadagi barcha fayllarni yuklang
   (main.py, config.py, database.py, locales.py, handlers/ papkasi,
   requirements.txt, Procfile).

## 4-qadam: Railway'da joylashtirish
1. **railway.app** ga kiring, GitHub akkountingiz orqali ro'yxatdan o'ting.
2. "New Project" → "Deploy from GitHub repo" → repongizni tanlang.
3. Railway avtomatik `requirements.txt`ni o'rnatadi.
4. **Variables** bo'limiga o'ting va quyidagilarni qo'shing:
   - `BOT_TOKEN` = BotFather'dan olgan token
   - `ADMIN_IDS` = sizning Telegram ID (bir nechta bo'lsa vergul bilan: `12345,67890`)
   - `PAYMENT_CARD_NUMBER` = to'lov qabul qilinadigan karta raqami
   - `PAYMENT_CARD_OWNER` = karta egasining F.I.Sh.
5. Deploy tugagach, bot avtomatik ishga tushadi (Procfile orqali).

## Bot qanday ishlaydi
- Foydalanuvchi `/start` bosadi → til tanlaydi (UZ/RU/EN).
- Premium yoki Stars tanlaydi → to'lov usulini tanlaydi:
  - **Karta orqali**: bot karta raqamini ko'rsatadi, foydalanuvchi to'lov
    screenshotini yuboradi → sizga (adminga) yuboriladi → siz
    ✅/❌ tugmasi bilan tasdiqlaysiz yoki rad etasiz.
  - **Telegram Stars orqali**: bot avtomatik invoice yuboradi, to'lov
    Telegram ichida amalga oshadi.
- Tasdiqlangan buyurtmadan so'ng, Stars/Premium'ni **siz qo'lda** (masalan
  Fragment.com orqali) foydalanuvchiga yetkazib berasiz — bot faqat
  buyurtma va to'lovni boshqaradi.

## Muhim eslatma
- Bu MVP (boshlang'ich) versiya: Click/Payme to'lovlari hozircha
  "kartaga o'tkazib, screenshot yuborish" tarzida ishlaydi — bu tezkor
  ishga tushirish uchun qulay. Keyinchalik Click/Payme rasmiy merchant
  API (shartnoma, kalitlar bilan) ulanib, avtomatlashtirish mumkin.
- Narxlarni `config.py` faylidagi `PREMIUM_PLANS` va `STARS_PACKAGES`
  ro'yxatlarida o'zgartirasiz.
- Ma'lumotlar bazasi SQLite (`bot.db`) — Railway'da doimiy saqlash uchun
  "Volume" qo'shishni tavsiya qilaman (Railway loyihasida Settings →
  Volumes), aks holda qayta deploy qilinganda buyurtmalar tarixi tozalanadi.
