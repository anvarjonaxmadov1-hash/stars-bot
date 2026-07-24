import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import BOT_TOKEN
import database as db
from handlers import start, catalog, payment, admin


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni qayta boshlash"),
        BotCommand(command="premium", description="Premium sotib olish"),
        BotCommand(command="stars", description="Stars sotib olish"),
        BotCommand(command="orders", description="Buyurtmalarim"),
        BotCommand(command="invite", description="Do'stlarni taklif qilish"),
        BotCommand(command="language", description="Tilni o'zgartirish"),
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(level=logging.INFO)

    await db.init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(payment.router)
    dp.include_router(admin.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
import os

