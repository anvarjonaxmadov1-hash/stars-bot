import re

from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery,
)
from aiogram.methods import GiftPremiumSubscription

import database as db
from locales import t
from config import (
    PREMIUM_PLANS, STARS_PACKAGES, PAYMENT_CARD_NUMBER, PAYMENT_CARD_OWNER,
    ADMIN_IDS, CRYPTO_WALLET, CRYPTO_NETWORK, USD_TO_UZS,
    FOREIGN_CARD_VISA, FOREIGN_CARD_MASTERCARD, FOREIGN_CARD_OWNER,
    REFERRAL_BONUS_AMOUNT,
)

router = Router()

PENDING_SCREENSHOT: dict[int, int] = {}


def find_item(callback_data: str):
    if callback_data.startswith("gprem_"):
        item_id = callback_data.replace("gprem_", "")
        plan = next((p for p in PREMIUM_PLANS if p["id"] == item_id), None)
        if plan:
            return f"{plan['months']} oylik Premium (🎁 Sovg'a)", plan["price_som"]
    elif callback_data.startswith("sprem_"):
        item_id = callback_data.replace("sprem_", "")
        plan = next((p for p in PREMIUM_PLANS if p["id"] == item_id), None)
        if plan:
            return f"{plan['months']} oylik Premium (👤 O'zim uchun)", plan["price_som"]
    elif callback_data.startswith("buy_star_"):
        item_id = callback_data.replace("buy_star_", "")
        pack = next((s for s in STARS_PACKAGES if s["id"] == item_id), None)
        if pack:
            return f"{pack['amount']} Stars", pack["price_som"]
    return None, None


def _get_plan_from_callback(callback_data: str):
    if callback_data.startswith("gprem_"):
        item_id = callback_data.replace("gprem_", "")
    elif callback_data.startswith("sprem_"):
        item_id = callback_data.replace("sprem_", "")
    else:
        return None
    return next((p for p in PREMIUM_PLANS if p["id"] == item_id), None)


async def notify_admin_new_order(bot: Bot, order_id: int, user_id: int, username: str | None, item: str, price: int, method_label: str):
    caption = t("uz", "new_order_admin", order_id=order_id, username=username or "-",
                user_id=user_id, item=item, price=f"{price:,}".replace(",", " "), method=method_label)
    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, caption)


async def credit_referral_bonus(bot: Bot, order_id: int, buyer_id: int):
    order = await db.get_order(order_id)
    if not order:
        return
    _, _, _, _, _, _, _, bonus_given = order
    if bonus_given:
        return

    referrer_id = await db.get_referrer(buyer_id)
    if not referrer_id:
        return

    await db.add_balance(referrer_id, REFERRAL_BONUS_AMOUNT)
    await db.mark_bonus_given(order_id)

    referrer_lang = await db.get_lang(referrer_id)
    try:
        await bot.send_message(
            referrer_id,
            t(referrer_lang, "referral_bonus_notice", amount=f"{REFERRAL_BONUS_AMOUNT:,}".replace(",", " ")),
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("gprem_") | F.data.startswith("sprem_") | F.data.startswith("buy_star_"))
async def choose_payment_method(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    item_name, price = find_item(callback.data)
    if not item_name:
        await callback.answer("Xatolik / Error", show_alert=True)
        return

    is_self_type = callback.data.startswith("sprem_")
    show_stars_button = True
    notice = ""

    if callback.data.startswith("gprem_"):
        plan = _get_plan_from_callback(callback.data)
        if plan and plan.get("price_stars_service") is None:
            show_stars_button = False
            notice = t(lang, "one_month_notice")
    elif is_self_type:
        show_stars_button = False
        notice = (
            "ℹ️ Bu buyurtma operator tomonidan akkauntingizga qo'lda kiritiladi. "
            "To'lovdan so'ng chek yuboring, operator siz bilan bog'lanadi.\n\n"
        )

    buttons = [
        [InlineKeyboardButton(text=t(lang, "pay_card"), callback_data=f"paycard_{callback.data}")],
        [InlineKeyboardButton(text=t(lang, "pay_foreign_card"), callback_data=f"payforeign_{callback.data}")],
    ]
    if show_stars_button:
        buttons.append([InlineKeyboardButton(text=t(lang, "pay_stars"), callback_data=f"paystars_{callback.data}")])
    buttons.append([InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu_back")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(notice + t(lang, "choose_payment"), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("paycard_"))
async def pay_with_card(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    lang = await db.get_lang(user_id)
    original = callback.data.replace("paycard_", "")
    item_name, price = find_item(original)

    balance = await db.get_balance(user_id)
    discount = min(balance, price)
    if discount > 0:
        await db.use_balance(user_id, discount)
    final_price = price - discount

    order_id = await db.create_order(user_id, item_name, price, "card", discount_used=discount)

    if final_price <= 0:
        await db.update_order_status(order_id, "paid")
        await callback.message.edit_text(t(lang, "fully_covered", order_id=order_id))
        await notify_admin_new_order(bot, order_id, user_id, callback.from_user.username, item_name, price, "Karta (balans bilan to'liq qoplandi)")
        await credit_referral_bonus(bot, order_id, user_id)
    else:
        PENDING_SCREENSHOT[user_id] = order_id
        text = t(lang, "order_created", order_id=order_id, price=f"{final_price:,}".replace(",", " "),
                 card=PAYMENT_CARD_NUMBER, owner=PAYMENT_CARD_OWNER)
        if discount > 0:
            text += t(lang, "discount_applied", discount=f"{discount:,}".replace(",", " "))
        await callback.message.edit_text(text)
    await callback.answer()


@router.callback_query(F.data.startswith("payforeign_"))
async def pay_with_foreign_card(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    lang = await db.get_lang(user_id)
    original = callback.data.replace("payforeign_", "")
    item_name, price_som = find_item(original)

    balance = await db.get_balance(user_id)
    discount = min(balance, price_som)
    if discount > 0:
        await db.use_balance(user_id, discount)
    final_price_som = price_som - discount

    order_id = await db.create_order(user_id, item_name, price_som, "foreign_card", discount_used=discount)

    if final_price_som <= 0:
        await db.update_order_status(order_id, "paid")
        await callback.message.edit_text(t(lang, "fully_covered", order_id=order_id))
        await notify_admin_new_order(bot, order_id, user_id, callback.from_user.username, item_name, price_som, "Visa/Mastercard (balans bilan to'liq qoplandi)")
        await credit_referral_bonus(bot, order_id, user_id)
    else:
        usd_amount = round(final_price_som / USD_TO_UZS, 2)
        PENDING_SCREENSHOT[user_id] = order_id
        text = t(lang, "foreign_card_order_created", order_id=order_id, usd=usd_amount,
                 visa=FOREIGN_CARD_VISA, mastercard=FOREIGN_CARD_MASTERCARD, owner=FOREIGN_CARD_OWNER)
        if discount > 0:
            text += t(lang, "discount_applied", discount=f"{discount:,}".replace(",", " "))
        await callback.message.edit_text(text)
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
    _, _, item, price, method, _, discount_used, _ = order
    amount_to_pay = price - discount_used

    await message.answer(t(lang, "screenshot_received", order_id=order_id))

    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{order_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{order_id}"),
        ]
    ])
    method_labels = {"crypto": "USDT", "foreign_card": "Visa/Mastercard"}
    method_label = method_labels.get(method, "Karta")
    caption = t(lang, "new_order_admin", order_id=order_id, username=message.from_user.username or "-",
                user_id=user_id, item=item, price=f"{amount_to_pay:,}".replace(",", " "), method=method_label)
    for admin_id in ADMIN_IDS:
        await bot.send_photo(admin_id, message.photo[-1].file_id, caption=caption, reply_markup=admin_keyboard)


@router.callback_query(F.data.startswith("paystars_"))
async def pay_with_stars(callback: CallbackQuery, bot: Bot):
    lang = await db.get_lang(callback.from_user.id)
    original = callback.data.replace("paystars_", "")
    item_name, price_som = find_item(original)

    if original.startswith("gprem_"):
        plan = _get_plan_from_callback(original)
        stars_amount = plan["price_stars_service"] if plan else max(1, round(price_som / 200))
    else:
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
    if not order:
        return
    _, user_id, item, price, method, _, _, _ = order

    match = re.match(r"(\d+) oylik Premium", item)
    if match and method == "telegram_stars":
        months = int(match.group(1))
        plan = next((p for p in PREMIUM_PLANS if p["months"] == months), None)
        if plan:
            try:
                await bot(GiftPremiumSubscription(
                    user_id=user_id,
                    month_count=months,
                    star_count=plan["gift_star_cost"],
                ))
                await db.update_order_status(order_id, "delivered")
                await bot.send_message(user_id, t(lang, "premium_delivered", order_id=order_id))
                await credit_referral_bonus(bot, order_id, user_id)
                return
            except Exception as e:
                for admin_id in ADMIN_IDS:
                    await bot.send_message(
                        admin_id,
                        f"⚠️ Avtomatik yetkazishda xatolik #{order_id} (user {user_id}): {e}\n"
                        f"Iltimos, qo'lda yetkazib bering.",
                    )
                return

    await notify_admin_new_order(bot, order_id, user_id, message.from_user.username, item, price, "Telegram Stars")
    await credit_referral_bonus(bot, order_id, user_id)
