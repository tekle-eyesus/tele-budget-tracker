from aiogram import Router, types, F
import calendar
from datetime import datetime
from sqlalchemy import select
from data.database import AsyncSessionLocal, Expense, User, Subscription 

router = Router()

@router.message(F.text == "🔮 Forecast")
async def generate_forecast(message: types.Message):
    user_id = message.from_user.id
    now = datetime.utcnow()
    
    start_date = datetime(now.year, now.month, 1)
    _, last_day = calendar.monthrange(now.year, now.month)
    
    async with AsyncSessionLocal() as session:
        query = select(Expense).where(
            Expense.user_id == user_id,
            Expense.timestamp >= start_date
        )
        result = await session.execute(query)
        expenses = result.scalars().all()

        user_result = await session.execute(select(User).where(User.user_id == user_id))
        user_settings = user_result.scalar_one_or_none()

        sub_result = await session.execute(select(Subscription).where(Subscription.user_id == user_id))
        subs = sub_result.scalars().all()

    if not expenses and not subs and not user_settings:
        await message.answer("⚠️ Not enough data yet. Set a /budget or add expenses/subscriptions first!")
        return

    # Calculations
    total_variable_spent = sum(ex.amount for ex in expenses)
    fixed_costs = sum(s.amount for s in subs)
    total_spent_so_far = total_variable_spent + fixed_costs
    
    budget = user_settings.budget_limit if user_settings else 0.0
    
    disposable_budget = budget - fixed_costs

    days_passed = now.day
    days_in_month = last_day
    days_remaining = days_in_month - days_passed
    if days_passed == 0: days_passed = 1

    daily_average = total_variable_spent / days_passed
    projected_variable = daily_average * days_in_month
    
    total_projected = projected_variable + fixed_costs
    
    top_category = "None"
    top_cat_amount = 0.0
    if expenses:
        category_totals = {}
        for ex in expenses:
            category_totals[ex.category] = category_totals.get(ex.category, 0) + ex.amount
        top_category = max(category_totals, key=category_totals.get)
        top_cat_amount = category_totals[top_category]

    progress_bar = ""
    percent = 0
    if budget > 0:
        percent = (total_spent_so_far / budget) * 100
        filled_slots = int(percent / 10)
        if filled_slots > 10: filled_slots = 10
        
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
        f"💸 Var. Spent: <code>${total_variable_spent:,.2f}</code>\n"
        f"📅 Daily Avg: <code>${daily_average:,.2f}</code>\n"
    )

    if budget > 0:
        text += f"🎯 Budget: <code>${budget:,.2f}</code>\n"
        text += f"🔄 Fixed Subs: <code>${fixed_costs:,.2f}</code>\n"
        text += f"{progress_bar}\n"

    text += (
        f"<b>🚀 Month-End Projection</b>\n"
        f"🔮 Estimate: <code>${total_projected:,.2f}</code>\n"
        f"──────────────────\n"
    )

    # ADVISOR LOGIC
    if budget > 0:
        if fixed_costs > budget:
             text += (
                f"🚨 <b>CRITICAL WARNING</b>\n"
                f"Your Subscriptions (<code>${fixed_costs:,.2f}</code>) exceed your Budget!\n"
                f"Increase your budget or cancel some subscriptions."
            )
        else:
            difference = budget - total_projected
            
            if difference < 0:
                remaining_safe = disposable_budget - total_variable_spent
                daily_limit = remaining_safe / (days_remaining if days_remaining > 0 else 1)
                
                if daily_limit < 0: daily_limit = 0 

                text += (
                    f"⚠️ <b>OVERSPEND WARNING</b>\n"
                    f"Projected over: <code>${abs(difference):,.2f}</code>\n\n"
                    f"💡 <b>Fix It:</b> Limit daily spending to:\n"
                    f"👉 <code>${daily_limit:,.2f} / day</code>"
                )
            else:
                text += (
                    f"✅ <b>EXCELLENT</b>\n"
                    f"On track to save: <code>${difference:,.2f}</code>\n"
                    f"Safe daily spend: <code>${(disposable_budget - total_variable_spent) / (days_remaining if days_remaining > 0 else 1):,.2f}</code>"
                )
    else:
        text += "<i>💡 Tip: Use '🎯 Set Budget' to unlock smart financial advice.</i>"

    if top_cat_amount > 0:
        text += f"\n\n🔻 <b>Top Drain:</b> {top_category} (<code>${top_cat_amount:,.2f}</code>)"

    await message.answer(text, parse_mode="HTML")