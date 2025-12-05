import io
import pandas as pd
from aiogram import Router, types, F
from sqlalchemy import select
from data.database import AsyncSessionLocal, Expense
from utils.keyboards import get_export_keyboard
from utils.pdf_generator import generate_receipt_pdf

router = Router()

@router.message(F.text == "📥 Export")
async def show_export_options(message: types.Message):
    await message.answer(
        "📂 <b>Export Data</b>\n\n"
        "Click the button below to download your expenses as a formal receipt.",
        reply_markup=get_export_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "download_pdf")
async def send_pdf_receipt(callback: types.CallbackQuery):
    await callback.answer("Generating receipt...") # Gives visual feedback immediately

    # Fetch all expenses for the user
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Expense).where(Expense.user_id == callback.from_user.id).order_by(Expense.timestamp.desc())
        )
        expenses = result.scalars().all()

    if not expenses:
        await callback.message.answer("⚠️ You have no expenses to generate a receipt.")
        return

    # Generate the PDF
    pdf_file = generate_receipt_pdf(callback.from_user.first_name, expenses)

    # BufferedInputFile allows sending 'in-memory' files without saving to disk
    input_file = types.BufferedInputFile(
        pdf_file.read(), 
        filename=f"receipt_{callback.from_user.id}.pdf"
    )

    await callback.message.answer_document(
        document=input_file,
        caption="🧾 Here is your expense receipt."
    )

@router.callback_query(F.data == "download_excel")
async def send_excel_report(callback: types.CallbackQuery):
    await callback.answer("Generating Excel...")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Expense).where(Expense.user_id == callback.from_user.id).order_by(Expense.timestamp.desc())
        )
        expenses = result.scalars().all()

    if not expenses:
        await callback.message.answer("⚠️ No data found.")
        return

    data = [
        {
            "Date": ex.timestamp.strftime("%Y-%m-%d %H:%M"),
            "Category": ex.category,
            "Amount": ex.amount,
            "ID": ex.id
        }
        for ex in expenses
    ]
    df = pd.DataFrame(data)

    output = io.BytesIO()
    # using 'openpyxl' engine to write .xlsx
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Expenses")
    
    output.seek(0)

    input_file = types.BufferedInputFile(output.read(), filename="expenses_report.xlsx")
    await callback.message.answer_document(
        document=input_file, 
        caption="📊 Here is your Excel report. You can open this in Google Sheets or Excel."
    )