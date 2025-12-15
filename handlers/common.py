from aiogram import Router, types
from aiogram.filters import Command
from utils.keyboards import get_main_menu
from aiogram.types import BufferedInputFile

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

@router.message(Command("template"))
async def cmd_template(message: types.Message):
    """
    Sends a sample CSV file for the user to fill out.
    """
    # Create a dummy CSV in memory
    csv_content = "amount,category,description\n12.50,Food,Lunch at cafe\n50.00,Transport,Uber ride"
    
    file = BufferedInputFile(csv_content.encode(), filename="template.csv")
    
    await message.answer_document(
        document=file,
        caption="📂 <b>Bulk Import Template</b>\n\n1. Download this file.\n2. Add your expenses.\n3. Send the file back here to import them!",
        parse_mode="HTML"
    )