from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select
from data.database import AsyncSessionLocal, User

router = Router()

@router.message(Command("budget"))
async def set_budget_command(message: types.Message):
    """
    Usage: /budget 500
    Sets the monthly budget limit for the user.
    """
    args = message.text.split()
    
    # Validation: Did they provide a number?
    if len(args) != 2:
        await message.answer("⚠️ Usage: `/budget 500` (Replace 500 with your limit)")
        return

    try:
        limit = float(args[1])
    except ValueError:
        await message.answer("❌ Please enter a valid number.")
        return

    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        # Check if user exists in DB
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()

        if user:
            # Update existing
            user.budget_limit = limit
        else:
            # Create new
            user = User(user_id=user_id, budget_limit=limit)
            session.add(user)
        
        await session.commit()

    await message.answer(f"✅ Monthly Budget set to: <b>${limit:,.2f}</b>", parse_mode="HTML")