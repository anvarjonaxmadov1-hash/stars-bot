from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command, CommandObject

import database as db
from locales import t

router = Router()


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
        [InlineKeyboardButton(text=t(lang, "btn_orders"), callback_data="menu_orders")],
        [InlineKeyboardButton(text=t(lang, "btn_invite"), callback_data="menu_invite")],
        [InlineKeyboardButton(text=t(lang, "btn_lang"), callback_data="menu_lang")],
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
    await message.answer(t(lang, "invite_text", link=link, count=count))


@router.callback_query(F.data == "menu_invite")
async def menu_invite(callback: CallbackQuery, bot: Bot):
    lang = await db.get_lang(callback.from_user.id)
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{callback.from_user.id}"
    count = await db.count_referrals(callback.from_user.id)
    await callback.message.edit_text(
        t(lang, "invite_text", link=link, count=count),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="menu_back")]]),
    )
    await callback.answer()


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
