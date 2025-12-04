from aiogram import Router, types
from aiogram.filters import Command
from utils.keyboards import get_main_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Entry point for the bot.
    """
    await message.answer(
        f"Hello {message.from_user.first_name}! 👋\n"
        "I am your Personal Finance Bot.\n"
        "Use the buttons below to track your expenses.",
        reply_markup=get_main_menu()
    )