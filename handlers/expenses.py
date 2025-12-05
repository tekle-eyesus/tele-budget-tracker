from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from data.database import AsyncSessionLocal, Expense
from utils.keyboards import get_category_keyboard, get_main_menu
from sqlalchemy import select

router = Router()

# Define States (Steps in the conversation)
class AddExpenseState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()

# 1. Triggered when user clicks "Add Expense"
@router.message(F.text == "💸 Add Expense")
async def start_add_expense(message: types.Message, state: FSMContext):
    await message.answer("Enter the amount (e.g., 15.50):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddExpenseState.waiting_for_amount)

# 2. User types amount
@router.message(AddExpenseState.waiting_for_amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount) # Save to memory
        await message.answer("Select a category:", reply_markup=get_category_keyboard())
        await state.set_state(AddExpenseState.waiting_for_category)
    except ValueError:
        await message.answer("Please enter a valid number (e.g. 100 or 10.5).")

# 3. User selects category -> Save to DB
@router.message(AddExpenseState.waiting_for_category)
async def process_category(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data['amount']
    category = message.text

    # Save to Database
    async with AsyncSessionLocal() as session:
        new_expense = Expense(user_id=message.from_user.id, amount=amount, category=category)
        session.add(new_expense)
        await session.commit()

    await message.answer(f"✅ Saved: ${amount} for {category}", reply_markup=get_main_menu())
    await state.clear()

# 4. View History
@router.message(F.text == "📜 History")
async def show_history(message: types.Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Expense).where(Expense.user_id == message.from_user.id).order_by(Expense.timestamp.desc()).limit(5)
        )
        expenses = result.scalars().all()

    if not expenses:
        await message.answer("No expenses found.")
        return

    text = "🗓 <b>Recent Expenses:</b>\n\n"
    for ex in expenses:
        text += f"▫️ {ex.category}: ${ex.amount} ({ex.timestamp.strftime('%Y-%m-%d')})\n"
    
    await message.answer(text, parse_mode="HTML")