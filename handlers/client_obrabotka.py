from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext
from states.mebel_bron import BronForm
from database import crud
from config import ID_ADMIN
from handlers.client_panel import start_cmd
import re

router = Router()

@router.callback_query(F.data.startswith("cat:"))
async def handle_category(callback: CallbackQuery):
    data = callback.data.split(":")[1]

    categories_without_subcats = {"столы", "тумбы", "матрасы", "шкафы"}
    subcats = {
        "спальная": ["🇷🇺 Российская", "🇹🇷 Турецкая"],
        "кухонная": ["📐 Прямая", "🔽 Угловая"],
        "мягкая": ["🇷🇺 Российская", "🇹🇷 Турецкая"],
        "кровати": ["🇷🇺 Российская", "🇹🇷 Турецкая"],
    }

    if data == "about":
        await callback.message.answer(
            "📞 Контакты:\n"
            "🏢 Компания по продаже мебели\n"
            "📍 Грозный, ул. Мебельная, 10\n"
            "📱 +7 (995) 800-89-95"
        )
        await callback.answer()
        return

    if data in categories_without_subcats:
        # Получаем категорию из БД по имени с emoji
        categories = crud.get_categories()
        category = next((c for c in categories if c.name.lower() == data), None)
        if category:
            await show_products(callback, category.id, subcat="")
        else:
            await callback.message.answer("❌ Категория не найдена.")
        await callback.answer()
        return

    if data not in subcats:
        await callback.message.answer("❌ Неизвестная категория.")
        await callback.answer()
        return

    buttons = [
        [InlineKeyboardButton(text=sub, callback_data=f"subcat:{data}:{sub.split()[1].lower()}")]
        for sub in subcats[data]
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="назад")])

    await callback.message.answer(
        f"Категория: {data.capitalize()}\nВыберите подкатегорию:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("subcat:"))
async def handle_subcat(callback: CallbackQuery):
    try:
        _, cat_code, subcat_code = callback.data.split(":", maxsplit=2)
    except ValueError:
        await callback.message.answer("❌ Некорректные данные подкатегории.")
        await callback.answer()
        return

    categories = crud.get_categories()
    category = next((c for c in categories if c.name.lower() == cat_code), None)
    if not category:
        await callback.message.answer("❌ Категория не найдена.")
        await callback.answer()
        return

    await show_products(callback, category.id, subcat_code)

@router.callback_query(F.data == "назад")
async def handle_back(callback: CallbackQuery):
    await start_cmd(callback.message)
    await callback.answer()

async def show_products(callback: CallbackQuery, category_id: int, subcat: str):
    products = crud.get_products_by_category(category_id, subcat)

    if not products:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="назад")]
        ])
        await callback.message.answer("⚠️ Товары пока не добавлены.", reply_markup=kb)
        await callback.answer()
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{p.title} — {p.price}₽", callback_data=f"prod:{p.id}")]
        for p in products
    ] + [[InlineKeyboardButton(text="⬅️ Назад", callback_data="назад")]])

    # Используем edit_message_reply_markup, чтобы не спамить чат
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except:
        await callback.message.answer("Выберите товар:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("prod:"))
async def product_card(callback: CallbackQuery):
    try:
        prod_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.message.answer("❌ Некорректный ID товара.")
        await callback.answer()
        return

    product = crud.get_product(prod_id)

    if not product:
        await callback.message.answer('❌ Товар не найден')
        await callback.answer()
        return

    media = []
    for i in range(1, 5):
        image = getattr(product, f"image{i}", None)
        if image:
            media.append(InputMediaPhoto(media=image))

    if media:
        if len(media) == 1:
            await callback.message.answer_photo(media[0].media)
        else:
            await callback.message.answer_media_group(media)

    text = (
        f"<b>{product.title}</b>\n\n"
        f"{product.description or 'Нет описания'}\n\n"
        f"🌍 <b>Страна:</b> {product.country or '—'}\n"
        f"📏 <b>Размеры:</b> {product.size or '—'}\n"
        f"💰 <b>Цена:</b> {product.price} ₽"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Задать вопрос", callback_data=f"chat:{product.id}")],
        [InlineKeyboardButton(text="📞 Консультация", callback_data=f"consult:{product.id}")],
        [InlineKeyboardButton(text="🛒 Оформить заказ", callback_data=f"bron:{product.id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="назад")]
    ])

    await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("bron:"))
async def start_bron(callback: CallbackQuery, state: FSMContext):
    try:
        product_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.message.answer("❌ Некорректный ID товара для заказа.")
        await callback.answer()
        return

    await state.update_data(product_id=product_id)
    await state.set_state(BronForm.waiting_for_name)
    await callback.message.answer("Введите ваше имя:")
    await callback.answer()


@router.message(BronForm.waiting_for_name)
async def bron_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(BronForm.waiting_for_phone)
    await message.answer("Введите номер телефона (например, +79991234567):")

@router.message(BronForm.waiting_for_phone)
async def bron_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not re.match(r"^\+7\d{10}$", phone):
        await message.answer("⚠️ Неверный формат. Попробуйте снова (пример: +79991234567)")
        return
    await state.update_data(phone=phone)
    await state.set_state(BronForm.waiting_for_comment)
    await message.answer("Комментарий (или '-' если без него):")

@router.message(BronForm.waiting_for_comment)
async def bron_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    comment = message.text if message.text != "-" else ""

    crud.create_order(
        user_id=message.from_user.id,
        name=data["name"],
        phone=data["phone"],
        product_id=data["product_id"],
        comment=comment
    )

    await message.answer("✅ Заказ оформлен! С вами скоро свяжутся.")
    await message.bot.send_message(
        chat_id=ID_ADMIN,
        text=(
            f"🆕 Новый заказ!\n"
            f"👤 Имя: {data['name']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"🛍 Товар: {crud.get_product(data['product_id']).title}\n"
            f"💬 Комментарий: {comment or '—'}"
        )
    )

    await state.clear()