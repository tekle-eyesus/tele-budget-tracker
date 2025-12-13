import asyncio
import logging
import os
import sys
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from data.database import init_db
from handlers import common, expenses, statistics, export, budget ,insights

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def health_check(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")

async def main():
    # 1. Init Database
    await init_db()

    # 2. Setup Bot & Dispatcher
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # 3. Register Routers
    dp.include_router(common.router)
    dp.include_router(statistics.router)
    dp.include_router(budget.router)
    dp.include_router(insights.router)
    dp.include_router(export.router)
    dp.include_router(expenses.router)

    # 4. Start the Fake Server (Background task)
    await start_web_server()

    # 5. Start Polling
    print("Bot is running...")
    # remove_webhook is useful if switching from other hosting methods
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")