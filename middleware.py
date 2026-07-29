from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import FORCE_SUB_CHANNEL
from locales import t
import database as db


async def is_subscribed(bot, user_id: int) -> bool:
    """Foydalanuvchi majburiy obuna kanaliga a'zo ekanligini tekshiradi."""
    if not FORCE_SUB_CHANNEL:
        return True
    try:
        member = await bot.get_chat_member(chat_id=FORCE_SUB_CHANNEL, user_id=user_id)
        return member.status not in ("left", "kicked")
    except Exception:
        # Agar tekshirib bo'lmasa (masalan bot kanalda admin emas), foydalanuvchini bloklamaymiz
        return True


class ForceSubMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        bot = data["bot"]
        user = data.get("event_from_user")

        if not user or not FORCE_SUB_CHANNEL:
            return await handler(event, data)

        # "Tekshirish" tugmasini har doim o'tkazamiz — u o'zi qayta tekshiradi
        if isinstance(event, CallbackQuery) and event.data == "check_sub":
            return await handler(event, data)

        if await is_subscribed(bot, user.id):
            return await handler(event, data)

        lang = await db.get_lang(user.id)
        channel_username = FORCE_SUB_CHANNEL.lstrip("@")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "btn_join_channel"), url=f"https://t.me/{channel_username}")],
            [InlineKeyboardButton(text=t(lang, "btn_check_sub"), callback_data="check_sub")],
        ])
        text = t(lang, "force_sub_text", channel=FORCE_SUB_CHANNEL)

        if isinstance(event, CallbackQuery):
            await event.answer()
            try:
                await event.message.edit_text(text, reply_markup=keyboard)
            except Exception:
                await event.message.answer(text, reply_markup=keyboard)
        elif isinstance(event, Message):
            await event.answer(text, reply_markup=keyboard)

        return  # handler chaqirilmaydi, obuna bo'lmaguncha
