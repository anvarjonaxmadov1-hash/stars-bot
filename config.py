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

# Taklif qilingan do'stning har bir tasdiqlangan buyurtmasi uchun taklif qiluvchiga beriladigan bonus (so'mda)
REFERRAL_BONUS_AMOUNT = int(os.getenv("REFERRAL_BONUS_AMOUNT", "100"))

# Majburiy obuna kanali (bo'sh qoldirsangiz, majburiy obuna o'chiq bo'ladi)
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "@premium_channeluz")

DB_PATH = "bot.db"
DATABASE_URL = os.getenv("DATABASE_URL", "")

# ==== MAHSULOTLAR ====
PREMIUM_PLANS = [
    {"id": "prem_1m", "months": 1, "price_som": 39999, "gift_star_cost": None, "price_stars_service": None},
    {"id": "prem_3m", "months": 3, "price_som": 151899, "gift_star_cost": 1000, "price_stars_service": 1100},
    {"id": "prem_6m", "months": 6, "price_som": 249000, "gift_star_cost": 1500, "price_stars_service": 1650},
    {"id": "prem_12m", "months": 12, "price_som": 399000, "gift_star_cost": 2500, "price_stars_service": 2750},
]

# Stars narxlari: tannarx 1 star = 240 so'm, ustama ~12 so'm/star (turli xil "marketing" oxiri bilan)
STARS_PACKAGES = [
    {"id": "st_50", "amount": 50, "price_som": 12490},
    {"id": "st_100", "amount": 100, "price_som": 24890},
    {"id": "st_150", "amount": 150, "price_som": 37290},
    {"id": "st_250", "amount": 250, "price_som": 62690},
    {"id": "st_350", "amount": 350, "price_som": 87890},
    {"id": "st_500", "amount": 500, "price_som": 125490},
    {"id": "st_750", "amount": 750, "price_som": 188690},
    {"id": "st_1000", "amount": 1000, "price_som": 251890},
    {"id": "st_1500", "amount": 1500, "price_som": 377290},
    {"id": "st_2500", "amount": 2500, "price_som": 629690},
    {"id": "st_5000", "amount": 5000, "price_som": 1259490},
    {"id": "st_10000", "amount": 10000, "price_som": 2519890},
    {"id": "st_25000", "amount": 25000, "price_som": 6299290},
    {"id": "st_50000", "amount": 50000, "price_som": 12599690},
    {"id": "st_100000", "amount": 100000, "price_som": 25199490},
    {"id": "st_150000", "amount": 150000, "price_som": 37799890},
]
