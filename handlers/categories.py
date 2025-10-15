# from aiogram import Router
# from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
# from database import crud

# router = Router()

# def main_menu_keyboard():
#     cats = crud.get_categories()
#     cat_map = {
#         "🛋 Мягкая мебель": "мягкая",
#         "🍳 Кухонная мебель": "кухонная",
#         "🛏 Спальная мебель": "спальная",
#         "📚 Столы и стулья": "столы",
#         "📺 Тумбы и комоды": "тумбы",
#         "🛏 Матрасы": "матрасы",
#         "🚪 Шкафы": "шкафы"
#     }
#     buttons = [
#         [InlineKeyboardButton(text=cat['name'], callback_data=f"cat:{cat_map.get(cat['name'], cat['id'])}")]
#          for cat in cats
#     ]
#     buttons.append([InlineKeyboardButton(text="ℹ️ О компании / Контакты", callback_data="cat:about")])
#     return InlineKeyboardMarkup(inline_keyboard=buttons)

# def subcategories_keyboard(category_key, subcats):
#     buttons = [
#         [InlineKeyboardButton(text=subcat, callback_data=f"subcat:{category_key}:{subcat.lower()}")] 
#         for subcat in subcats
#     ]
#     buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")])
#     return InlineKeyboardMarkup(inline_keyboard=buttons)

# @router.callback_query(lambda c: c.data and c.data.startswith("cat:"))
# async def process_category_callback(callback_query: CallbackQuery):
#     category_key = callback_query.data.split(":")[1]
#     if category_key == "about":
#         await callback_query.message.edit_text("Информация о компании и контакты здесь.")
#     else:
#         subcats = crud.get_subcategories(category_key)
#         if not subcats:
#             # Здесь можно вывести товары или сообщение, что подкатегорий нет
#             await callback_query.answer("Товары для этой категории пока не добавлены.")
#         else:
#             keyboard = subcategories_keyboard(category_key, subcats)
#             await callback_query.message.edit_text(f"Выберите подкатегорию для {category_key}:", reply_markup=keyboard)
#     await callback_query.answer()

# @router.callback_query(lambda c: c.data == "back_to_main")
# async def process_back_to_main(callback_query: CallbackQuery):
#     keyboard = main_menu_keyboard()
#     await callback_query.message.edit_text("🏠 Главное меню:\nВыберите категорию мебели:", reply_markup=keyboard)
#     await callback_query.answer()
