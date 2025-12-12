from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from data.database import AsyncSessionLocal, User
from utils.keyboards import get_main_menu

router = Router()

class BudgetState(StatesGroup):
    waiting_for_amount = State()

@router.message(F.text == "🎯 Set Budget")
async def start_set_budget(message: types.Message, state: FSMContext):
    await message.answer(
        "Please enter your monthly budget target (e.g., 500 or 1000):", 
        reply_markup=types.ReplyKeyboardRemove() # Hide menu temporarily
    )
    await state.set_state(BudgetState.waiting_for_amount)

@router.message(BudgetState.waiting_for_amount)
async def process_budget_amount(message: types.Message, state: FSMContext):
    try:
        limit = float(message.text)
    except ValueError:
        await message.answer("❌ That doesn't look like a number. Please try again (e.g., 1000).")
        return

    if limit < 0:
        await message.answer("❌ Budget cannot be negative.")
        return

    user_id = message.from_user.id
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()

        if user:
            user.budget_limit = limit
        else:
            user = User(user_id=user_id, budget_limit=limit)
            session.add(user)
        
        await session.commit()

    await message.answer(
        f"✅ Monthly Budget updated to: <b>${limit:,.2f}</b>\n"
        "Go to '📊 Stats' to see your progress!",
        reply_markup=get_main_menu(), # Bring back the menu
        parse_mode="HTML"
    )
    
    await state.clear()