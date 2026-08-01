from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

import database as db
from locales import t
from config import PREMIUM_PLANS, STARS_PACKAGES

router = Router()


def back_button(lang: str, to: str = "menu_back") -> InlineKeyboardButton:
    return InlineKeyboardButton(text=t(lang, "btn_back"), callback_data=to)


def _grid(buttons: list, columns: int = 2) -> list:
    """Tugmalar ro'yxatini berilgan ustun soniga bo'lib qatorlarga ajratadi."""
    return [buttons[i:i + columns] for i in range(0, len(buttons), columns)]


def premium_keyboard(lang: str) -> InlineKeyboardMarkup:
    items = [
        InlineKeyboardButton(
            text=t(lang, "premium_item", months=p["months"], price=f'{p["price_som"]:,}'.replace(",", " ")),
            callback_data=f"buy_prem_{p['id']}",
        )
        for p in PREMIUM_PLANS
    ]
    rows = _grid(items, columns=2)
    rows.append([back_button(lang)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def stars_keyboard(lang: str) -> InlineKeyboardMarkup:
    items = [
        InlineKeyboardButton(
            text=t(lang, "stars_item", amount=s["amount"], price=f'{s["price_som"]:,}'.replace(",", " ")),
            callback_data=f"buy_star_{s['id']}",
        )
        for s in STARS_PACKAGES
    ]
    rows = _grid(items, columns=2)
    rows.append([back_button(lang)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def build_orders_text(lang: str, user_id: int) -> str:
    orders = await db.get_user_orders(user_id)
    if not orders:
        return t(lang, "no_orders")
    status_map = {"pending": "status_pending", "paid": "status_paid", "rejected": "status_rejected"}
    lines = [t(lang, "your_orders")]
    for order_id, item, price, status in orders:
        lines.append(t(lang, "order_line", id=order_id, item=item, price=f"{price:,}".replace(",", " "),
                        status=t(lang, status_map.get(status, "status_pending"))))
    return "\n".join(lines)


@router.callback_query(F.data == "menu_premium")
async def show_premium(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    await callback.message.edit_text(t(lang, "choose_premium"), reply_markup=premium_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "menu_stars")
async def show_stars(callback: CallbackQuery, bot: Bot):
    lang = await db.get_lang(callback.from_user.id)
    await callback.answer()
    await bot.send_message(callback.from_user.id, "🌟")
    await callback.message.answer(t(lang, "choose_stars"), reply_markup=stars_keyboard(lang))


@router.callback_query(F.data == "menu_orders")
async def show_orders(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    text = await build_orders_text(lang, callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[back_button(lang)]]))
    await callback.answer()


@router.message(Command("premium"))
async def cmd_premium(message: Message):
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t(lang, "choose_premium"), reply_markup=premium_keyboard(lang))


@router.message(Command("stars"))
async def cmd_stars(message: Message):
    lang = await db.get_lang(message.from_user.id)
    await message.answer("🌟")
    await message.answer(t(lang, "choose_stars"), reply_markup=stars_keyboard(lang))


@router.message(Command("orders"))
async def cmd_orders(message: Message):
    lang = await db.get_lang(message.from_user.id)
    text = await build_orders_text(lang, message.from_user.id)
    await message.answer(text)


@router.message(Command("language"))
async def cmd_language(message: Message):
    from handlers.start import lang_keyboard
    await message.answer(t("uz", "choose_lang"), reply_markup=lang_keyboard())
