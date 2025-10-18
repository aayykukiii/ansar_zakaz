from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import ID_ADMIN
from handlers.commands import start_cmd

router = Router()

@router.message(Command("start"), F.from_user.id == ID_ADMIN)
async def admin_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить категорию", callback_data="admin_add_category")],
        [InlineKeyboardButton(text="🪑 Добавить мебель", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="❌ Удалить мебель", callback_data="admin_delete_product")],
        [InlineKeyboardButton(text="📂 Список категорий", callback_data="admin_list_categories")],
        [InlineKeyboardButton(text="📋 Заявки", callback_data="admin_show_orders")]
    ])
    await message.answer(
        f"🔧 <b>Панель администратора</b>\n\n"
        f"Здравствуйте, <b>{message.from_user.full_name}</b> (<code>{message.from_user.id}</code>)\n\n"
        f"Выберите действие из меню ниже:",
        reply_markup=kb,
        parse_mode="HTML"
    )
