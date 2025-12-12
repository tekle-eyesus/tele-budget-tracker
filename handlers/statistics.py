import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from aiogram import Router, types, F
from sqlalchemy import select
from data.database import AsyncSessionLocal, Expense, User
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
    period = callback.data.split("_")[1]
    start_date, end_date, title = get_date_range(period)

    await callback.message.edit_text(f"Generating chart for: {title}...")

    async with AsyncSessionLocal() as session:
        query = select(Expense).where(
            Expense.user_id == callback.from_user.id,
            Expense.timestamp >= start_date,
            Expense.timestamp <= end_date
        )
        result = await session.execute(query)
        expenses = result.scalars().all()

        # Fetch User Budget
        user_result = await session.execute(select(User).where(User.user_id == callback.from_user.id))
        user_settings = user_result.scalar_one_or_none()

    if not expenses:
        await callback.message.edit_text(f"⚠️ No expenses found for {title}.")
        return

    # Aggregate Data
    data = {}
    total_spent = 0
    for ex in expenses:
        data[ex.category] = data.get(ex.category, 0) + ex.amount
        total_spent += ex.amount

    # --- Budget Progress Logic ---
    budget_text = ""
    if period == "current" and user_settings and user_settings.budget_limit > 0:
        limit = user_settings.budget_limit
        percent = (total_spent / limit) * 100
        
        # Create Bar: [▓▓▓▓▓░░░░░]
        filled_slots = int(percent / 10) 
        if filled_slots > 10: filled_slots = 10 # Cap at 100% visually
        
        bar = "▓" * filled_slots + "░" * (10 - filled_slots)
        
        status_emoji = "🟢" if percent < 80 else "🟠" if percent < 100 else "🔴"
        
        budget_text = (
            f"\n\n🎯 <b>Budget Goal:</b> ${limit:,.0f}\n"
            f"{status_emoji} <b>[{bar}] {percent:.1f}%</b>"
        )

    labels = [f"{k} (${v:.0f})" for k, v in data.items()]
    values = list(data.values())

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(f"{title}\nTotal: ${total_spent:.2f}")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    photo_file = types.BufferedInputFile(buf.read(), filename="chart.png")
    
    await callback.message.delete()
    await callback.message.answer_photo(
        photo_file, 
        caption=f"📊 <b>{title}</b>\nTotal Spent: <b>${total_spent:.2f}</b>{budget_text}", 
        parse_mode="HTML"
    )