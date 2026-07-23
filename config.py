import os

# ==== ASOSIY SOZLAMALAR ====
# Bu qiymatlarni Railway'da "Variables" bo'limiga qo'yasiz (kodga yozmang!)
BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKEN_BU_YERGA")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# To'lov uchun karta raqami (Click/Payme/Uzcard/Humo orqali qo'lda to'lov)
PAYMENT_CARD_NUMBER = os.getenv("PAYMENT_CARD_NUMBER", "8600 XXXX XXXX XXXX")
PAYMENT_CARD_OWNER = os.getenv("PAYMENT_CARD_OWNER", "F. I. Sh.")

DB_PATH = "bot.db"

# ==== MAHSULOTLAR ====
# narx so'mda (karta orqali to'lov uchun)
PREMIUM_PLANS = [
    {"id": "prem_3m", "months": 3, "price_som": 149000, "price_stars_service": 250},
    {"id": "prem_6m", "months": 6, "price_som": 249000, "price_stars_service": 450},
    {"id": "prem_12m", "months": 12, "price_som": 399000, "price_stars_service": 750},
]

STARS_PACKAGES = [
    {"id": "st_50", "amount": 50, "price_som": 19000},
    {"id": "st_100", "amount": 100, "price_som": 36000},
    {"id": "st_250", "amount": 250, "price_som": 85000},
    {"id": "st_500", "amount": 500, "price_som": 165000},
    {"id": "st_1000", "amount": 1000, "price_som": 320000},
]
