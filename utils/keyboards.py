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
            [KeyboardButton(text="💸 Add Expense")], 
            [KeyboardButton(text="📊 Stats"), KeyboardButton(text="🔮 Forecast")],
            [KeyboardButton(text="📜 History"), KeyboardButton(text="🗑 Delete")],     
            [KeyboardButton(text="🎯 Set Budget"), KeyboardButton(text="📥 Export")]
        ],
        resize_keyboard=True
    )

def get_category_keyboard():
    categories = ["Food", "Transport", "Shopping", "Bills", "Other"]
    keyboard = [[KeyboardButton(text=c) for c in categories[i:i+2]] for i in range(0, len(categories), 2)]
    keyboard.append([KeyboardButton(text="✏️ Custom")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_delete_keyboard(expenses):
    builder = InlineKeyboardBuilder()
    for expense in expenses:
        button_text = f"{expense.category} - ${expense.amount}"
        builder.button(text=button_text, callback_data=f"del_{expense.id}")
    builder.button(text="❌ Cancel", callback_data="del_cancel")
    builder.adjust(1)
    return builder.as_markup()

def get_export_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📄 PDF Receipt", callback_data="download_pdf"),
                InlineKeyboardButton(text="📊 Excel Report", callback_data="download_excel")
            ]
        ]
    )

def get_stats_period_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 This Month", callback_data="stats_current"),
                InlineKeyboardButton(text="🗓 Last Month", callback_data="stats_previous")
            ],
            [
                InlineKeyboardButton(text="∞ All Time", callback_data="stats_all")
            ]
        ]
    )