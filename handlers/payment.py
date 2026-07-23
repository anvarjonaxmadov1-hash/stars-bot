from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery,
)

import database as db
from locales import t
from config import PREMIUM_PLANS, STARS_PACKAGES, PAYMENT_CARD_NUMBER, PAYMENT_CARD_OWNER, ADMIN_IDS

router = Router()

PENDING_SCREENSHOT: dict[int, int] = {}


def find_item(callback_data: str):
    if callback_data.startswith("buy_prem_"):
        item_id = callback_data.replace("buy_prem_", "")
        plan = next((p for p in PREMIUM_PLANS if p["id"] == item_id), None)
        if plan:
            return f"{plan['months']} oylik Premium", plan["price_som"]
    elif callback_data.startswith("buy_star_"):
        item_id = callback_data.replace("buy_star_", "")
        pack = next((s for s in STARS_PACKAGES if s["id"] == item_id), None)
        if pack:
            return f"{pack['amount']} Stars", pack["price_som"]
    return None, None


@router.callback_query(F.data.startswith("buy_prem_") | F.data.startswith("buy_star_"))
async def choose_payment_method(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    item_name, price = find_item(callback.data)
    if not item_name:
        await callback.answer("Xatolik / Error", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "pay_card"), callback_data=f"paycard_{callback.data}")],
        [InlineKeyboardButton(text=t(lang, "pay_stars"), callback_data=f"paystars_{callback.data}")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu_back")],
    ])
    await callback.message.edit_text(t(lang, "choose_payment"), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("paycard_"))
async def pay_with_card(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    original = callback.data.replace("paycard_", "")
    item_name, price = find_item(original)

    order_id = await db.create_order(callback.from_user.id, item_name, price, "card")
    PENDING_SCREENSHOT[callback.from_user.id] = order_id

    await callback.message.edit_text(
        t(lang, "order_created", order_id=order_id, price=f"{price:,}".replace(",", " "),
          card=PAYMENT_CARD_NUMBER, owner=PAYMENT_CARD_OWNER)
    )
    await callback.answer()


@router.message(F.photo)
async def receive_screenshot(message: Message, bot: Bot):
    user_id = message.from_user.id
    if user_id not in PENDING_SCREENSHOT:
        return

    lang = await db.get_lang(user_id)
    order_id = PENDING_SCREENSHOT.pop(user_id)
    order = await db.get_order(order_id)
    if not order:
        return
    _, _, item, price, method, _ = order

    await message.answer(t(lang, "screenshot_received", order_id=order_id))

    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{order_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{order_id}"),
        ]
    ])
    caption = t(lang, "new_order_admin", order_id=order_id, username=message.from_user.username or "-",
                user_id=user_id, item=item, price=f"{price:,}".replace(",", " "), method="Karta")
    for admin_id in ADMIN_IDS:
        await bot.send_photo(admin_id, message.photo[-1].file_id, caption=caption, reply_markup=admin_keyboard)


@router.callback_query(F.data.startswith("paystars_"))
async def pay_with_stars(callback: CallbackQuery, bot: Bot):
    lang = await db.get_lang(callback.from_user.id)
    original = callback.data.replace("paystars_", "")
    item_name, price_som = find_item(original)

    stars_amount = max(1, round(price_som / 200))

    order_id = await db.create_order(callback.from_user.id, item_name, price_som, "telegram_stars")

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=t(lang, "invoice_title", item=item_name),
        description=t(lang, "invoice_desc", item=item_name),
        payload=f"order_{order_id}",
        currency="XTR",
        prices=[LabeledPrice(label=item_name, amount=stars_amount)],
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot):
    payload = message.successful_payment.invoice_payload
    order_id = int(payload.replace("order_", ""))
    await db.update_order_status(order_id, "paid")

    lang = await db.get_lang(message.from_user.id)
    await message.answer(t(lang, "payment_success", order_id=order_id))

    order = await db.get_order(order_id)
    if order:
        _, user_id, item, price, method, _ = order
        for admin_id in ADMIN_IDS:
            await bot.send_message(
                admin_id,
                t("uz", "new_order_admin", order_id=order_id, username=message.from_user.username or "-",
                  user_id=user_id, item=item, price=f"{price:,}".replace(",", " "), method="Telegram Stars"),
            )
