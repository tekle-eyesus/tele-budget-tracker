from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, delete
from data.database import AsyncSessionLocal, Expense
from utils.keyboards import get_category_keyboard, get_main_menu, get_delete_keyboard # <--- Imported new function

router = Router()

class AddExpenseState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_custom_category = State()

@router.message(F.text == "💸 Add Expense")
async def start_add_expense(message: types.Message, state: FSMContext):
    await message.answer("Enter the amount (e.g., 15.50):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddExpenseState.waiting_for_amount)

@router.message(AddExpenseState.waiting_for_amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await message.answer("Select a category:", reply_markup=get_category_keyboard())
        await state.set_state(AddExpenseState.waiting_for_category)
    except ValueError:
        await message.answer("Please enter a valid number.")

@router.message(AddExpenseState.waiting_for_category)
async def process_category(message: types.Message, state: FSMContext):
    if message.text == "✏️ Custom":
        await message.answer("Please type your custom category name:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(AddExpenseState.waiting_for_custom_category)
        return
    await save_expense(message, state, category_name=message.text)


@router.message(AddExpenseState.waiting_for_custom_category)
async def process_custom_category(message: types.Message, state: FSMContext):
    await save_expense(message, state, category_name=message.text)

async def save_expense(message: types.Message, state: FSMContext, category_name: str):
    data = await state.get_data()
    amount = data['amount']

    async with AsyncSessionLocal() as session:
        new_expense = Expense(user_id=message.from_user.id, amount=amount, category=category_name)
        session.add(new_expense)
        await session.commit()

    await message.answer(f"✅ Saved: ${amount} for {category_name}", reply_markup=get_main_menu())
    await state.clear()

@router.message(F.text == "📜 History")
async def show_history(message: types.Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Expense).where(Expense.user_id == message.from_user.id).order_by(Expense.timestamp.desc()).limit(10)
        )
        expenses = result.scalars().all()
    
    if not expenses:
        await message.answer("No expenses found.")
        return
        
    text = "🗓 <b>Recent Expenses:</b>\n"
    for ex in expenses:
        text += f"▫️ {ex.category}: ${ex.amount}\n"
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🗑 Delete")
async def start_delete_process(message: types.Message):
    async with AsyncSessionLocal() as session:
        # Fetch last 5 expenses to keep the list manageable
        result = await session.execute(
            select(Expense).where(Expense.user_id == message.from_user.id).order_by(Expense.timestamp.desc()).limit(5)
        )
        expenses = result.scalars().all()

    if not expenses:
        await message.answer("No expenses to delete.")
        return

    # Send the Inline Keyboard
    await message.answer(
        "Select an expense to delete:", 
        reply_markup=get_delete_keyboard(expenses)
    )

@router.callback_query(F.data.startswith("del_"))
async def process_delete_callback(callback: types.CallbackQuery):
    action = callback.data.split("_")[1] # "del_15" -> "15" OR "del_cancel" -> "cancel"

    # Handle Cancel
    if action == "cancel":
        await callback.message.delete() # Remove the menu
        await callback.answer("Cancelled") # Tiny popup
        return

    # Handle Deletion
    expense_id = int(action)
    
    async with AsyncSessionLocal() as session:
        # Check if expense exists (and belongs to this user for security)
        result = await session.execute(select(Expense).where(Expense.id == expense_id))
        expense = result.scalar_one_or_none()
        
        if expense:
            await session.delete(expense)
            await session.commit()
            await callback.message.edit_text(f"✅ Deleted expense: {expense.category} - ${expense.amount}")
        else:
            await callback.message.edit_text("❌ Expense not found (already deleted?).")
    
    await callback.answer() 