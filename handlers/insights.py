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

    # Report Text
    text = (
        f"🔮 <b>End-of-Month Projection</b>\n"
        f"📅 Date: {now.strftime('%B %d')}\n\n"
        
        f"📉 <b>Current Status:</b>\n"
        f"• Spent so far: <b>${total_spent:,.2f}</b>\n"
        f"• Avg. Daily Spend: <b>${daily_average:,.2f}</b>\n\n"
        
        f"🚀 <b>Forecast:</b>\n"
        f"At this rate, you will spend <b>${projected_total:,.2f}</b> by month end.\n"
    )

    if budget > 0:
        difference = budget - projected_total
        text += f"🎯 <b>Budget Goal:</b> ${budget:,.2f}\n"
        
        if difference < 0:
            text += f"⚠️ <b>WARNING:</b> You are on track to overspend by <b>${abs(difference):,.2f}</b>!\n"
            text += f"💡 <b>Advice:</b> Try to spend less than <b>${(budget - total_spent) / (days_remaining if days_remaining > 0 else 1):,.2f}</b> per day for the rest of the month."
        else:
            text += f"✅ <b>Great Job!</b> You are on track to save <b>${difference:,.2f}</b>."
    else:
        text += "\n<i>(Set a /budget to get smart advice)</i>"

    text += f"\n\n🍔 <b>Top Drain:</b> {top_category} (${top_cat_amount:,.2f})"

    await message.answer(text, parse_mode="HTML")