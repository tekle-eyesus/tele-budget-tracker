from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Main Menu Keyboard
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💸 Add Expense"), KeyboardButton(text="📊 Stats")],
            [KeyboardButton(text="📜 History")]
        ],
        resize_keyboard=True
    )

# Categories for expenses
def get_category_keyboard():
    categories = ["Food", "Transport", "Shopping", "Bills", "Other"]
    # Create rows of 2 buttons
    keyboard = [[KeyboardButton(text=c) for c in categories[i:i+2]] for i in range(0, len(categories), 2)]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)