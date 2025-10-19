from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database import crud
from states.admin_states import AddProductFSM, AddCategoryFSM
from handlers.client_panel import start_cmd

router = Router()

# Обработка кнопки "Добавить категорию"
@router.callback_query(F.data == "admin_add_category")
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AddCategoryFSM.waiting_for_name)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить", callback_data="admin_back")]
    ])
    text = (
        "🆕 Создание новой категории мебели\n\n"
        "Введите название категории.\n\n"
        "🔹 Совет: добавьте эмодзи в начале названия — это делает меню заметнее.\n\n"
        "Примеры:\n"
        "🛏️ Спальная мебель\n"
        "🍳 Кухонная мебель\n"
        "🛋️ Мягкая мебель\n"
        "📚 Столы и стулья\n"
        "📺 Тумбы и комоды\n"
        "🛏️ Кровати\n"
        "🛏️ Матрасы\n"
        "🚪 Шкафы\n\n"
        "Отправьте название или нажмите «Отменить»."
    )
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

# Обработка отмены / возврата в меню
@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await start_cmd(callback.message)
    await callback.answer()

# Получение названия категории
@router.message(AddCategoryFSM.waiting_for_name)
async def process_category_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("❗️ Название категории не может быть пустым. Попробуйте снова:")
        return

    # Генерируем код — например, из имени в нижний регистр без пробелов
    code = name.lower().replace(" ", "_")

    # Проверяем, есть ли уже категория с таким кодом
    existing = crud.get_category_by_code(code)
    if existing:
        await message.answer("❗️ Такая категория уже существует. Попробуйте другое название.")
        return

    cat = crud.add_category(name=name, code=code, parent_id=None)
    await message.answer(f"✅ Категория <b>{cat.name}</b> успешно добавлена!", parse_mode="HTML")
    await state.clear()
    await start_cmd(message)

# ====== Добавление мебели ======

@router.callback_query(F.data == "admin_add_product")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AddProductFSM.waiting_for_title)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])
    await callback.message.answer("🛋 Введите название товара:", reply_markup=kb)
    await callback.answer()
    

@router.message(AddProductFSM.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if not title:
        await message.answer("❗️ Название не может быть пустым. Попробуйте снова:")
        return
    await state.update_data(title=title)

    categories = crud.get_categories(parent_id=None)
    if not categories:
        await message.answer("⚠️ Нет категорий в базе. Добавьте категорию сначала.")
        await state.clear()
        return

    buttons = [
        [InlineKeyboardButton(text=cat.name, callback_data=f"admin_cat_select:{cat.id}")]
        for cat in categories
    ]
    # Добавляем кнопку назад в отдельный ряд
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await state.set_state(AddProductFSM.waiting_for_category)
    await message.answer("Выберите категорию:", reply_markup=kb)


@router.callback_query(F.data.startswith("admin_cat_select:"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split(":", 1)[1])
    category = crud.get_category_by_id(cat_id)
    if not category:
        await callback.message.answer("❌ Категория не найдена, выберите ещё раз.")
        await callback.answer()
        return

    await state.update_data(category_id=cat_id)

    subcats = crud.get_categories(parent_id=cat_id)
    if subcats:
        kb = InlineKeyboardMarkup(row_width=1)
        for sub in subcats:
            kb.insert(InlineKeyboardButton(text=sub.name, callback_data=f"admin_subcat_select:{sub.id}"))
        kb.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back"))
        await state.set_state(AddProductFSM.waiting_for_subcategory)
        await callback.message.answer("Выберите подкатегорию:", reply_markup=kb)
    else:
        await state.update_data(subcategory=None)
        await state.set_state(AddProductFSM.waiting_for_country)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
        ])
        await callback.message.answer("Введите страну производства:", reply_markup=kb)

    await callback.answer()

@router.callback_query(F.data.startswith("admin_subcat_select:"))
async def process_subcategory(callback: CallbackQuery, state: FSMContext):
    subcat_id = int(callback.data.split(":", 1)[1])
    subcat = crud.get_category_by_id(subcat_id)
    if not subcat:
        await callback.message.answer("❌ Подкатегория не найдена, выберите ещё раз.")
        await callback.answer()
        return

    await state.update_data(subcategory=subcat.code)
    await state.set_state(AddProductFSM.waiting_for_country)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]])
    await callback.message.answer("Введите страну производства:", reply_markup=kb)
    await callback.answer()

@router.message(AddProductFSM.waiting_for_country)
async def process_country(message: Message, state: FSMContext):
    country = message.text.strip()
    if not country:
        await message.answer("❗️ Страна не может быть пустой. Попробуйте снова:")
        return
    await state.update_data(country=country)

    await state.set_state(AddProductFSM.waiting_for_type)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]])
    await message.answer("Введите тип (например, прямая, угловая):", reply_markup=kb)

@router.message(AddProductFSM.waiting_for_type)
async def process_type(message: Message, state: FSMContext):
    type_ = message.text.strip()
    if not type_:
        await message.answer("❗️ Тип не может быть пустым. Попробуйте снова:")
        return
    await state.update_data(type_=type_)

    await state.set_state(AddProductFSM.waiting_for_price)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]])
    await message.answer("Введите цену (целое число):", reply_markup=kb)

@router.message(AddProductFSM.waiting_for_price)
async def process_price(message: Message, state: FSMContext):
    price_text = message.text.strip()
    if not price_text.isdigit():
        await message.answer("❗️ Цена должна быть числом. Попробуйте снова:")
        return
    price = int(price_text)
    await state.update_data(price=price)

    await state.set_state(AddProductFSM.waiting_for_size)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]])
    await message.answer("Введите размер (например, 200x150):", reply_markup=kb)

@router.message(AddProductFSM.waiting_for_size)
async def process_size(message: Message, state: FSMContext):
    size = message.text.strip()
    if not size:
        await message.answer("❗️ Размер не может быть пустым. Попробуйте снова:")
        return
    await state.update_data(size=size)

    await state.set_state(AddProductFSM.waiting_for_description)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]])
    await message.answer("Введите описание товара:", reply_markup=kb)

@router.message(AddProductFSM.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    description = message.text.strip()
    await state.update_data(description=description)

    await state.set_state(AddProductFSM.waiting_for_images)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Готово", callback_data="admin_finish_product")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])
    await message.answer(
        "Отправьте фотографии товара (можно несколько сообщений с фото). "
        "Когда закончите, нажмите кнопку «Готово».", 
        reply_markup=kb
    )

@router.message(AddProductFSM.waiting_for_images, F.content_type == "photo")
async def process_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    images = data.get("images", [])
    # Получаем файл id самого большого размера фото
    photo = message.photo[-1]
    images.append(photo.file_id)
    await state.update_data(images=images)
    await message.answer(f"Фото добавлено ({len(images)} шт.). Отправьте ещё или нажмите «Готово».")

@router.callback_query(F.data == "admin_finish_product")
async def finish_adding_product(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    required_fields = ["title", "category_id", "country", "type_", "price", "size", "description"]
    if not all(field in data for field in required_fields):
        await callback.message.answer("❗️ Не все данные заполнены, начните заново.")
        await state.clear()
        await callback.answer()
        return

    images = data.get("images", [])
    # Берём до 4 фото, остальные игнорируем
    images = images[:4]

    product = crud.add_product(
        title=data["title"],
        category_id=data["category_id"],
        subcategory=data.get("subcategory"),
        country=data["country"],
        type_=data["type_"],
        price=data["price"],
        images=images,
        description=data["description"],
        size=data["size"]
    )

    await callback.message.answer(f"✅ Товар <b>{product.title}</b> успешно добавлен!", parse_mode="HTML")
    await state.clear()
    # Показываем админ-меню (вызов команды)
    await start_cmd(callback.message)
    await callback.answer()


# Список категорий
@router.callback_query(F.data == "admin_list_categories")
async def list_categories(callback: CallbackQuery):
    categories = crud.get_categories(parent_id=None)
    if not categories:
        await callback.message.answer("📂 Категории пока не созданы.")
        await callback.answer()
        return

    text = "📂 Список категорий:\n\n"
    for cat in categories:
        text += f"• {cat.name} (ID: {cat.id})\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

# Заявки (orders)
@router.callback_query(F.data == "admin_show_orders")
async def show_orders(callback: CallbackQuery):
    orders = crud.get_orders()
    if not orders:
        await callback.message.answer("📋 Заявок пока нет.")
        await callback.answer()
        return

    for o in orders:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="В работу", callback_data=f"admin_order:{o.id}:work"),
                InlineKeyboardButton(text="Закрыта", callback_data=f"admin_order:{o.id}:close")
            ]
        ])
        text = (
            f"ID: {o.id}\n"
            f"Имя: {o.name}\n"
            f"Телефон: {o.phone}\n"
            f"Товар: {o.product.title}\n"
            f"Статус: {o.status}\n"
            f"Комментарий: {o.comment or '—'}\n"
        )
        await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("admin_order:"))
async def change_order_status(callback: CallbackQuery):
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.message.answer("❗️ Некорректная команда.")
        await callback.answer()
        return
    order_id = int(parts[1])
    action = parts[2]
    order = crud.get_order(order_id)
    if not order:
        await callback.message.answer("❌ Заказ не найден.")
        await callback.answer()
        return

    if action == "work":
        crud.update_order_status(order.id, "В работе")
        new_status = "В работе"
    elif action == "close":
        crud.update_order_status(order.id, "Закрыта")
        new_status = "Закрыта"
    else:
        await callback.answer()
        return

    await callback.message.answer(f"✅ Статус заказа {order.id} обновлён на «{new_status}».")
    await callback.answer()

# Удаление мебели – простая заглушка или можно вывести список
@router.callback_query(F.data == "admin_delete_product")
async def delete_product(callback: CallbackQuery):
    products = crud.get_all_products()
    if not products:
        await callback.message.answer("🗑 Товаров нет для удаления.")
        await callback.answer()
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Удалить {p.title}", callback_data=f"admin_delete:{p.id}")]
        for p in products
    ] + [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back")]
    ])
    await callback.message.answer("🗑 Выберите товар для удаления:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("admin_delete:"))
async def perform_delete(callback: CallbackQuery):
    prod_id = int(callback.data.split(":", 1)[1])
    success = crud.delete_product(prod_id)
    if success:
        await callback.message.answer(f"✅ Товар ID {prod_id} удалён.")
    else:
        await callback.message.answer(f"❌ Ошибка: товар ID {prod_id} не найден или удалить не удалось.")
    await callback.answer()
