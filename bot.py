import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from data.database import init_db
from handlers import common, expenses, statistics, export 

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def main():
    await init_db()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(expenses.router)
    dp.include_router(statistics.router)
    dp.include_router(export.router)

    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")