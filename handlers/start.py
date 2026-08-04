from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent,
)
from aiogram.filters import CommandStart, Command, CommandObject

import database as db
from locales import t
from config import ADMIN_IDS
from middleware import is_subscribed

router = Router()

# user_id -> True, yordam xabari kutilayotgan foydalanuvchilar uchun
PENDING_SUPPORT: dict[int, bool] = {}


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]
    ])


@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery, bot: Bot):
    lang = await db.get_lang(callback.from_user.id)
    if await is_subscribed(bot, callback.from_user.id):
        await callback.answer("✅")
        await callback.message.edit_text(t("uz", "choose_lang"), reply_markup=lang_keyboard())
    else:
        await callback.answer(t(lang, "still_not_subscribed"), show_alert=True)


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_premium"), callback_data="menu_premium")],
        [InlineKeyboardButton(text=t(lang, "btn_stars"), callback_data="menu_stars")],
        [InlineKeyboardButton(text=t(lang, "btn_orders"), callback_data="menu_orders")],
        [InlineKeyboardButton(text=t(lang, "btn_invite"), callback_data="menu_invite")],
        [InlineKeyboardButton(text=t(lang, "btn_balance"), callback_data="menu_balance")],
        [InlineKeyboardButton(text=t(lang, "btn_support"), callback_data="menu_support")],
    ])


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    referred_by = None
    if command.args and command.args.startswith("ref_"):
        try:
            ref_id = int(command.args.replace("ref_", ""))
            if ref_id != message.from_user.id:
                referred_by = ref_id
        except ValueError:
            pass

    await db.set_user(message.from_user.id, message.from_user.username or "", referred_by)
    await message.answer(t("uz", "choose_lang"), reply_markup=lang_keyboard())


@router.message(Command("invite"))
async def cmd_invite(message: Message, bot: Bot):
    lang = await db.get_lang(message.from_user.id)
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{message.from_user.id}"
    count = await db.count_referrals(message.from_user.id)
    balance = await db.get_balance(message.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_share"), switch_inline_query="invite")],
    ])
    await message.answer(
        t(lang, "invite_text", link=link, count=count, balance=f"{balance:,}".replace(",", " ")),
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "menu_invite")
async def menu_invite(callback: CallbackQuery, bot: Bot):
    lang = await db.get_lang(callback.from_user.id)
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{callback.from_user.id}"
    count = await db.count_referrals(callback.from_user.id)
    balance = await db.get_balance(callback.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_share"), switch_inline_query="invite")],
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu_back")],
    ])
    await callback.message.edit_text(
        t(lang, "invite_text", link=link, count=count, balance=f"{balance:,}".replace(",", " ")),
        reply_markup=keyboard,
    )
    await callback.answer()


@router.inline_query()
async def handle_inline_query(inline_query: InlineQuery, bot: Bot):
    user_id = inline_query.from_user.id
    lang = await db.get_lang(user_id)
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{user_id}"

    result = InlineQueryResultArticle(
        id="invite",
        title=t(lang, "share_title"),
        description=t(lang, "share_desc"),
        input_message_content=InputTextMessageContent(message_text=t(lang, "share_message", link=link)),
    )
    await inline_query.answer([result], cache_time=1, is_personal=True)


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    await db.set_lang(callback.from_user.id, lang)
    name = callback.from_user.first_name or "friend"
    await callback.message.edit_text(t(lang, "welcome", name=name))
    await callback.message.answer(t(lang, "main_menu"), reply_markup=main_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "menu_lang")
async def change_language(callback: CallbackQuery):
    await callback.message.edit_text(t("uz", "choose_lang"), reply_markup=lang_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu_back")
async def back_to_menu(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    await callback.message.edit_text(t(lang, "main_menu"), reply_markup=main_menu_keyboard(lang))
    await callback.answer()


async def _build_orders_summary(user_id: int) -> str:
    orders = await db.get_user_orders(user_id)
    if not orders:
        return "— (buyurtmalar yo'q)"
    lines = []
    for order_id, item, price, status in orders:
        lines.append(f"#{order_id} | {item} | {price:,} so'm | {status}".replace(",", " "))
    return "\n".join(lines)


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    lang = await db.get_lang(message.from_user.id)
    balance = await db.get_balance(message.from_user.id)
    await message.answer(t(lang, "balance_text", balance=f"{balance:,}".replace(",", " ")))


@router.callback_query(F.data == "menu_balance")
async def menu_balance(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    balance = await db.get_balance(callback.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu_back")],
    ])
    await callback.message.edit_text(t(lang, "balance_text", balance=f"{balance:,}".replace(",", " ")), reply_markup=keyboard)
    await callback.answer()


@router.message(Command("support"))
async def cmd_support(message: Message):
    lang = await db.get_lang(message.from_user.id)
    PENDING_SUPPORT[message.from_user.id] = True
    await message.answer(t(lang, "support_prompt"))


@router.callback_query(F.data == "menu_support")
async def menu_support(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    PENDING_SUPPORT[callback.from_user.id] = True
    await callback.message.edit_text(
        t(lang, "support_prompt"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu_back")]]),
    )
    await callback.answer()


def is_pending_support(message: Message) -> bool:
    return message.from_user.id in PENDING_SUPPORT


@router.message(F.text, is_pending_support)
async def handle_support_message(message: Message, bot: Bot):
    user_id = message.from_user.id
    PENDING_SUPPORT.pop(user_id, None)
    lang = await db.get_lang(user_id)
    orders_summary = await _build_orders_summary(user_id)

    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            t("uz", "support_admin_msg", username=message.from_user.username or "-",
              user_id=user_id, message=message.text, orders=orders_summary),
        )
    await message.answer(t(lang, "support_sent"))
