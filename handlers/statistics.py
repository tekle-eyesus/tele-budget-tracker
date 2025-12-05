import matplotlib.pyplot as plt
import io
from aiogram import Router, types, F
from sqlalchemy import select
from data.database import AsyncSessionLocal, Expense

router = Router()

@router.message(F.text == "📊 Stats")
async def show_stats(message: types.Message):
    async with AsyncSessionLocal() as session:
        # Fetch all expenses for user
        result = await session.execute(select(Expense).where(Expense.user_id == message.from_user.id))
        expenses = result.scalars().all()

    if not expenses:
        await message.answer("No data to show stats.")
        return

    # Aggregate data
    data = {}
    for ex in expenses:
        data[ex.category] = data.get(ex.category, 0) + ex.amount

    # Generate Chart
    labels = list(data.keys())
    values = list(data.values())

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%')
    plt.title("Expenses by Category")

    # Save to memory buffer (BioIO) so we don't create files on disk
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Send Photo
    photo_file = types.BufferedInputFile(buf.read(), filename="chart.png")
    await message.answer_photo(photo_file, caption="Here is your spending breakdown.")