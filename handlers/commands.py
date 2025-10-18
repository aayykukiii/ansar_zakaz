from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import crud
from config import ID_ADMIN

router = Router()

@router.message(Command("start"))
async def start_cmd(message: Message):
    if message.from_user.id == ID_ADMIN:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить категорию", callback_data="admin_add_category")],
            [InlineKeyboardButton(text="🪑 Добавить мебель", callback_data="admin_add_product")],
            [InlineKeyboardButton(text="❌ Удалить мебель", callback_data="admin_delete_product")],
            [InlineKeyboardButton(text="📂 Список категорий", callback_data="admin_list_categories")],
            [InlineKeyboardButton(text="📋 Заявки", callback_data="admin_show_orders")]
        ])
        await message.answer(
            f"🔧 <b>Панель администратора</b>\n\n"
            f"Здравствуйте, {message.from_user.full_name} (<code>{message.from_user.id}</code>)\n\n"
            f"Выберите действие из меню ниже:",
            reply_markup=kb,
            parse_mode="HTML"
        )
    else:
        cat_map = {
            "🛋 Мягкая мебель": "myagkaya",
            "🍳 Кухонная мебель": "kuhonnaya",
            "🛏 Спальная мебель": "spalnaya",
            "🛏 Кровати": "krovati",
            "📚 Столы и стулья": "stoly_stulya",
            "📺 Тумбы и комоды": "tumby_komody",
            "🛏 Матрасы": "matrasy",
            "🚪 Шкафы": "shkafy",
        }

        cats = crud.get_categories(parent_id=None)
        if not cats:
            for name, code in cat_map.items():
                crud.add_category(name=name, code=code, parent_id=None)
            cats = crud.get_categories(parent_id=None)

        kb_buttons = [
            [InlineKeyboardButton(text=cat.name, callback_data=f"cat:{cat.code}")]
            for cat in cats
        ]
        kb_buttons.append([InlineKeyboardButton(text="ℹ️ О компании / Контакты", callback_data="cat:about")])

        kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
        await message.answer("🏠 Главное меню:\nВыберите категорию мебели:", reply_markup=kb)
