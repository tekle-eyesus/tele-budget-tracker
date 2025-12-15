from aiogram import Router, types, F
import calendar
from datetime import datetime
from sqlalchemy import select
from data.database import AsyncSessionLocal, Expense, User

router = Router()

@router.message(F.text == "🔮 Forecast")
async def generate_forecast(message: types.Message):
    user_id = message.from_user.id
    now = datetime.utcnow()
    
    start_date = datetime(now.year, now.month, 1)
    # Get the last day of the current month
    _, last_day = calendar.monthrange(now.year, now.month)
    
    # Fetch Data
    async with AsyncSessionLocal() as session:
        query = select(Expense).where(
            Expense.user_id == user_id,
            Expense.timestamp >= start_date
        )
        result = await session.execute(query)
        expenses = result.scalars().all()

        # Get Budget
        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user_settings = user_result.scalar_one_or_none()

    if not expenses:
        await message.answer("⚠️ Not enough data yet to make a prediction. Add some expenses first!")
        return

    total_spent = sum(ex.amount for ex in expenses)
    budget = user_settings.budget_limit if user_settings else 0.0
    
    days_passed = now.day
    days_in_month = last_day
    days_remaining = days_in_month - days_passed
    
    if days_passed == 0: days_passed = 1

    daily_average = total_spent / days_passed
    projected_total = daily_average * days_in_month
    
    # Find Top Spending Category
    category_totals = {}
    for ex in expenses:
        category_totals[ex.category] = category_totals.get(ex.category, 0) + ex.amount
    top_category = max(category_totals, key=category_totals.get)
    top_cat_amount = category_totals[top_category]

    progress_bar = ""
    percent = 0
    if budget > 0:
        percent = (total_spent / budget) * 100
        filled_slots = int(percent / 10)
        if filled_slots > 10: filled_slots = 10
        
        # Color indicator based on health
        health_icon = "🟢"
        if percent > 80: health_icon = "🟠"
        if percent >= 100: health_icon = "🔴"
        
        bar = "▓" * filled_slots + "░" * (10 - filled_slots)
        progress_bar = f"{health_icon} <b>[{bar}] {percent:.0f}%</b>\n"
    
    text = (
        f"🔮 <b>FINANCIAL FORECAST</b>\n"
        f"<i>Analysis for {now.strftime('%B %Y')}</i>\n"
        f"──────────────────\n"
        
        f"<b>📊 Current Status</b>\n"
        f"💸 Spent: <code>${total_spent:,.2f}</code>\n"
        f"📅 Daily Avg: <code>${daily_average:,.2f}</code>\n"
    )

    if budget > 0:
        text += f"🎯 Budget: <code>${budget:,.2f}</code>\n"
        text += f"{progress_bar}\n"

    text += (
        f"<b>🚀 Month-End Projection</b>\n"
        f"🔮 Estimate: <code>${projected_total:,.2f}</code>\n"
        f"──────────────────\n"
    )

    if budget > 0:
        difference = budget - projected_total
        
        if difference < 0:
            # Overspending Warning
            daily_limit = (budget - total_spent) / (days_remaining if days_remaining > 0 else 1)
            if daily_limit < 0: daily_limit = 0 

            text += (
                f"🚨 <b>CRITICAL WARNING</b>\n"
                f"You are projected to overspend by <code>${abs(difference):,.2f}</code>!\n\n"
                f"💡 <b>Fix It:</b> Cut your spending to \n"
                f"👉 <code>${daily_limit:,.2f} / day</code>"
            )
        else:
            # On Track
            text += (
                f"✅ <b>EXCELLENT</b>\n"
                f"You are on track to save <code>${difference:,.2f}</code> this month.\n"
                f"Keep it up!"
            )
    else:
        text += "<i>💡 Tip: Use '🎯 Set Budget' to unlock smart financial advice.</i>"

    # Top Drain
    text += f"\n\n🔻 <b>Top Drain:</b> {top_category} (<code>${top_cat_amount:,.2f}</code>)"

    await message.answer(text, parse_mode="HTML")