from aiogram import Router, F
from aiogram.filters import Command
from database import crud
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import ID_ADMIN

router = Router()

@router.message(Command("start"))
async def start_cmd(message: Message):
    cat_map = {
        "🛋 Мягкая мебель": "мягкая",
        "🍳 Кухонная мебель": "кухонная",
        "🛏 Спальная мебель": "спальная",
        "📚 Столы и стулья": "столы",
        "📺 Тумбы и комоды": "тумбы",
        "🛏 Матрасы": "матрасы",
        "🚪 Шкафы": "шкафы",
    }

    cats = crud.get_categories()

    if not cats:
        for name, code in cat_map.items():
            crud.add_category(name, code)


    keyboard_buttons = [
        [InlineKeyboardButton(text=cat.name, callback_data=f"cat:{cat_map.get(cat.name, cat.id)}")]
        for cat in cats
    ]

    keyboard_buttons.append([InlineKeyboardButton(text="ℹ️ О компании / Контакты", callback_data="cat:about")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await message.answer("🏠 Главное меню:\nВыберите категорию мебели:", reply_markup=keyboard)