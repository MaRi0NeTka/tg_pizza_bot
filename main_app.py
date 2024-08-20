import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from dotenv import load_dotenv, find_dotenv 
load_dotenv(find_dotenv())

from database.engine import create_db, session_maker

from handlers.user_private import user_router
from handlers.channel_commond import channel_router
from handlers.admin_private import admin_router
from middlewares.db import DataBaseSession


bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(user_router)
dp.include_router(channel_router)
dp.include_router(admin_router)


async def main():
    #await drop_db()
    await create_db()
    dp.update.middleware(DataBaseSession(session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())