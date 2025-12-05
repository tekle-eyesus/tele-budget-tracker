from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💸 Add Expense"), KeyboardButton(text="📊 Stats")],
            [KeyboardButton(text="📜 History"), KeyboardButton(text="🗑 Delete")]
        ],
        resize_keyboard=True
    )

def get_category_keyboard():
    categories = ["Food", "Transport", "Shopping", "Bills", "Other"]
    keyboard = [[KeyboardButton(text=c) for c in categories[i:i+2]] for i in range(0, len(categories), 2)]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Dynamic Inline Keyboard for Deletion
def get_delete_keyboard(expenses):
    """
    Creates a list of buttons, where each button represents an expense.
    The callback_data stores the ID of the expense (e.g., 'del_5').
    """
    builder = InlineKeyboardBuilder()
    
    for expense in expenses:
        # Button Text: "Food - $15.0"
        button_text = f"{expense.category} - ${expense.amount}"
        # Callback Data: "del_ID" (e.g. del_12)
        builder.button(text=button_text, callback_data=f"del_{expense.id}")
    
    # Add a Cancel button at the bottom
    builder.button(text="❌ Cancel", callback_data="del_cancel")
    
    
    builder.adjust(1)
    return builder.as_markup()