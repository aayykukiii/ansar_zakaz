from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import crud

router = Router()

@router.message(Command("start"))
async def start_cmd(message: Message):
    cats = crud.get_categories()

    if not cats:
        default_categories = [
            "🛋 Мягкая мебель",
            "🍳 Кухонная мебель",
            "🛏 Спальная мебель",
            "📚 Столы и стулья",
            "📺 Тумбы и комоды",
            "🛏 Матрасы",
            "🚪 Шкафы"
        ]
        for name in default_categories:
            crud.add_category(name)
        cats = crud.get_categories()

    cat_map = {
        "🛋 Мягкая мебель": "мягкая",
        "🍳 Кухонная мебель": "кухонная",
        "🛏 Спальная мебель": "спальная",
        "📚 Столы и стулья": "столы",
        "📺 Тумбы и комоды": "тумбы",
        "🛏 Матрасы": "матрасы",
        "🚪 Шкафы": "шкафы"
    }

    keyboard_buttons = [
        [InlineKeyboardButton(text=cat['name'], callback_data=f"cat:{cat_map.get(cat['name'], cat['id'])}")]
        for cat in cats
    ]

    keyboard_buttons.append([
        InlineKeyboardButton(text="ℹ️ О компании / Контакты", callback_data="cat:about")
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await message.answer("🏠 Главное меню:\nВыберите категорию мебели:", reply_markup=keyboard)
