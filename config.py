import os

# ==== ASOSIY SOZLAMALAR ====
# Bu qiymatlarni Railway'da "Variables" bo'limiga qo'yasiz (kodga yozmang!)
BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKEN_BU_YERGA")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# To'lov uchun karta raqami (Click/Payme/Uzcard/Humo orqali qo'lda to'lov)
PAYMENT_CARD_NUMBER = os.getenv("PAYMENT_CARD_NUMBER", "8600 XXXX XXXX XXXX")
PAYMENT_CARD_OWNER = os.getenv("PAYMENT_CARD_OWNER", "F. I. Sh.")

# Chet eldagi mijozlar uchun kripto (USDT) orqali to'lov
CRYPTO_WALLET = os.getenv("CRYPTO_WALLET", "TXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
CRYPTO_NETWORK = os.getenv("CRYPTO_NETWORK", "USDT (TRC20)")
# 1 USD necha so'm ekanini taxminiy ko'rsatish uchun (kripto narxini so'mdan USD'ga aylantirish)
USD_TO_UZS = int(os.getenv("USD_TO_UZS", "12700"))

# Chet eldagi mijozlar uchun xalqaro Visa/Mastercard (dollar hisobida)
FOREIGN_CARD_VISA = os.getenv("FOREIGN_CARD_VISA", "4111 XXXX XXXX XXXX")
FOREIGN_CARD_MASTERCARD = os.getenv("FOREIGN_CARD_MASTERCARD", "5412 XXXX XXXX XXXX")
FOREIGN_CARD_OWNER = os.getenv("FOREIGN_CARD_OWNER", "F. I. Sh.")

DB_PATH = "bot.db"

# ==== MAHSULOTLAR ====
# narx so'mda (karta/USDT orqali to'lov uchun)
# gift_star_cost — Telegramning rasmiy narxi (bot shu miqdorni o'z Stars balansidan sarflaydi,
# buni o'zgartirib bo'lmaydi: 3 oy=1000, 6 oy=1500, 12 oy=2500)
# price_stars_service — mijozdan Stars orqali to'lov olinganda so'raladigan narx (albatta gift_star_cost'dan yuqori bo'lishi kerak)
PREMIUM_PLANS = [
    {"id": "prem_1m", "months": 1, "price_som": 65000, "gift_star_cost": None, "price_stars_service": None},
    {"id": "prem_3m", "months": 3, "price_som": 149000, "gift_star_cost": 1000, "price_stars_service": 1100},
    {"id": "prem_6m", "months": 6, "price_som": 249000, "gift_star_cost": 1500, "price_stars_service": 1650},
    {"id": "prem_12m", "months": 12, "price_som": 399000, "gift_star_cost": 2500, "price_stars_service": 2750},
]

STARS_PACKAGES = [
    {"id": "st_50", "amount": 50, "price_som": 19000},
    {"id": "st_100", "amount": 100, "price_som": 36000},
    {"id": "st_250", "amount": 250, "price_som": 85000},
    {"id": "st_500", "amount": 500, "price_som": 165000},
    {"id": "st_1000", "amount": 1000, "price_som": 320000},
]
