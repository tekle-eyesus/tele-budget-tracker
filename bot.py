import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from data.database import init_db
from handlers import common, expenses, statistics

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def main():
    # 1. Init Database
    await init_db()

    # 2. Setup Bot & Dispatcher
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # 3. Register Routers
    dp.include_router(common.router)
    dp.include_router(expenses.router)
    dp.include_router(statistics.router)

    # 4. Start Polling
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")