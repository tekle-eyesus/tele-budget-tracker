import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from aiogram import Router, types, F
from sqlalchemy import select
from data.database import AsyncSessionLocal, Expense
from utils.keyboards import get_stats_period_keyboard

router = Router()

@router.message(F.text == "📊 Stats")
async def ask_time_period(message: types.Message):
    await message.answer(
        "Select the time period for your report:",
        reply_markup=get_stats_period_keyboard()
    )

def get_date_range(period):
    now = datetime.utcnow()
    
    if period == "current":
        start_date = datetime(now.year, now.month, 1)
        end_date = now
        title = f"Expenses - {now.strftime('%B %Y')}"
    
    elif period == "previous":
        first_of_this_month = datetime(now.year, now.month, 1)
        end_date = first_of_this_month - timedelta(seconds=1)
        start_date = datetime(end_date.year, end_date.month, 1)
        title = f"Expenses - {start_date.strftime('%B %Y')}"
        
    else: # "all"
        start_date = datetime.min
        end_date = datetime.max
        title = "Expenses - All Time"
        
    return start_date, end_date, title

@router.callback_query(F.data.startswith("stats_"))
async def generate_stats(callback: types.CallbackQuery):
    period = callback.data.split("_")[1] # "current", "previous", or "all"
    start_date, end_date, title = get_date_range(period)

    await callback.message.edit_text(f"Generating chart for: {title}...")

    # Query DB with Date Filter
    async with AsyncSessionLocal() as session:
        # WHERE timestamp >= start AND timestamp <= end
        query = select(Expense).where(
            Expense.user_id == callback.from_user.id,
            Expense.timestamp >= start_date,
            Expense.timestamp <= end_date
        )
        result = await session.execute(query)
        expenses = result.scalars().all()

    if not expenses:
        await callback.message.edit_text(f"⚠️ No expenses found for {title}.")
        return

    # Aggregate Data
    data = {}
    total_spent = 0
    for ex in expenses:
        data[ex.category] = data.get(ex.category, 0) + ex.amount
        total_spent += ex.amount

    # Generate Chart
    labels = [f"{k} (${v:.1f})" for k, v in data.items()] # Add amount to label
    values = list(data.values())

    plt.figure(figsize=(6, 6))
    # 'autopct' adds percentages to the slices
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(f"{title}\nTotal: ${total_spent:.2f}")

    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Send Result
    photo_file = types.BufferedInputFile(buf.read(), filename="chart.png")
    
    # Delete the "Generating..." message and send photo
    await callback.message.delete()
    await callback.message.answer_photo(photo_file, caption=f"📊 <b>{title}</b>\nTotal Spent: <b>${total_spent:.2f}</b>", parse_mode="HTML")