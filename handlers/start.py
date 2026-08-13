from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent, FSInputFile,
)
from aiogram.filters import CommandStart, Command, CommandObject

import database as db
from locales import t
from middleware import is_subscribed

router = Router()

# Bannerlar
MAIN_BANNER_PATH = "assets/banner_main.png"
PROFILE_BANNER_PATH = "assets/banner_profile.png"

CHANNEL_URL = "https://t.me/premium_channeluz"
REVIEWS_URL = "https://t.me/uz7_reviews"
SUPPORT_URL = "https://t.me/uz7sp_bot"


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]
    ])


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_premium"), callback_data="menu_premium")],
        [InlineKeyboardButton(text=t(lang, "btn_stars"), callback_data="menu_stars")],
        [InlineKeyboardButton(text=t(lang, "btn_invite"), callback_data="menu_invite")],
        [InlineKeyboardButton(text=t(lang, "btn_profile"), callback_data="menu_profile")],
        [
            InlineKeyboardButton(text=t(lang, "btn_channel"), url=CHANNEL_URL),
            InlineKeyboardButton(text=t(lang, "btn_reviews"), url=REVIEWS_URL),
        ],
        [InlineKeyboardButton(text=t(lang, "btn_support"), url=SUPPORT_URL)],
    ])


def profile_back_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu_back")]
    ])


async def send_main_menu(bot: Bot, chat_id: int, lang: str, name: str):
    caption = t(lang, "welcome", name=name) + "\n\n" + t(lang, "main_menu")

    try:
        photo = FSInputFile(MAIN_BANNER_PATH)

        await bot.send_photo(
            chat_id,
            photo,
            caption=caption,
            reply_markup=main_menu_keyboard(lang)
        )

    except Exception:
        await bot.send_message(
            chat_id,
            caption,
            reply_markup=main_menu_keyboard(lang)
)@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery, bot: Bot):
    lang = await db.get_lang(callback.from_user.id)

    if await is_subscribed(bot, callback.from_user.id):
        await callback.answer("✅")
        await callback.message.edit_text(
            t("uz", "choose_lang"),
            reply_markup=lang_keyboard()
        )
    else:
        await callback.answer(
            t(lang, "still_not_subscribed"),
            show_alert=True
        )


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

    await db.set_user(
        message.from_user.id,
        message.from_user.username or "",
        referred_by
    )

    await message.answer(
        t("uz", "choose_lang"),
        reply_markup=lang_keyboard()
    )


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, bot: Bot):
    lang = callback.data.split("_")[1]

    await db.set_lang(callback.from_user.id, lang)

    name = callback.from_user.first_name or "friend"

    await callback.message.delete()

    await send_main_menu(
        bot,
        callback.from_user.id,
        lang,
        name
    )

    await callback.answer()


@router.callback_query(F.data == "menu_profile")
async def menu_profile(callback: CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)

    user_id = callback.from_user.id
    username = callback.from_user.username or t(
        lang,
        "profile_no_username"
    )

    full_name = callback.from_user.full_name or "-"

    balance = await db.get_balance(user_id)
    referrals = await db.count_referrals(user_id)
    orders_count = await db.count_orders(user_id)


    text = t(
        lang,
        "profile_text",
        name=full_name,
        username=username,
        user_id=user_id,
        balance=f"{balance:,}".replace(",", " "),
        referrals=referrals,
        orders=orders_count,
    )


    try:
        photo = FSInputFile(PROFILE_BANNER_PATH)

        await callback.message.delete()

        await callback.message.answer_photo(
            photo,
            caption=text,
            reply_markup=profile_back_keyboard(lang)
        )

    except Exception:
        await callback.message.answer(
            text,
            reply_markup=profile_back_keyboard(lang)
        )

    await callback.answer()


@router.callback_query(F.data == "menu_back")
async def back_to_menu(callback: CallbackQuery, bot: Bot):
    lang = await db.get_lang(callback.from_user.id)

    name = callback.from_user.first_name or "friend"

    try:
        await callback.message.delete()
    except Exception:
        pass

    await send_main_menu(
        bot,
        callback.from_user.id,
        lang,
        name
    )

    await callback.answer()
