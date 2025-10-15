from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext
from states.mebel_bron import BronForm
from database import crud
from config import ID_ADMIN
import re

router = Router()

# Обработка категорий
@router.callback_query(F.data.startswith("cat:"))
async def handle_category(callback: CallbackQuery):
    data = callback.data.split(":")[1]

    if data == "about":
        await callback.message.answer(
            "📞 Контакты:\n"
            "🏢 Компания по продаже мебели\n"
            "📍 Грозный, ул. Мебельная, 10\n"
            "📱 +7 (995) 800-89-95"
        )
        await callback.answer()
        return

    # Подкатегории
    subcats = {
        "спальная": ["🇷🇺 Российская", "🇹🇷 Турецкая", "🛏 Кровати"],
        "кухонная": ["📐 Прямая", "🔽 Угловая"],
        "мягкая": ["🇷🇺 Российская", "🇹🇷 Турецкая"],
        "столы": ["🇷🇺 Российская", "🇹🇷 Турецкая"],
        "тумбы": ["🇷🇺 Российская", "🇹🇷 Турецкая"],
        "матрасы": ["🇷🇺 Российская", "🇹🇷 Турецкая"],
        "шкафы": ["🇷🇺 Российская", "🇹🇷 Турецкая"]
    }

    if data not in subcats:
        await callback.message.answer("❌ Неизвестная категория.")
        await callback.answer()
        return

    buttons = [
        [InlineKeyboardButton(text=sub, callback_data=f"subcat:{data}:{sub.split()[1].lower()}")]
        for sub in subcats[data]
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="назад")])

    await callback.message.answer(f"Категория: {data.capitalize()}\nВыберите подкатегорию:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

# Подкатегория
@router.callback_query(F.data.startswith("subcat:"))
async def handle_subcat(callback: CallbackQuery):
    _, cat_code, subcat_code = callback.data.split(":")

    # Вложенные подкатегории
    if (cat_code, subcat_code) == ("мягкая", "российская"):
        buttons = [
            [InlineKeyboardButton(text="Прямая", callback_data="subsub:мягкая:российская:прямая")],
            [InlineKeyboardButton(text="Угловая", callback_data="subsub:мягкая:российская:угловая")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="cat:мягкая")]
        ]
        await callback.message.answer("Выберите тип мягкой мебели:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        await callback.answer()
        return

    await show_products(callback, cat_code, subcat_code)

# Вложенная подкатегория
@router.callback_query(F.data.startswith("subsub:"))
async def handle_subsub(callback: CallbackQuery):
    _, cat_code, subcat_code, subsub = callback.data.split(":")
    await show_products(callback, cat_code, f"{subcat_code}_{subsub}")

# Назад
@router.callback_query(F.data == "назад")
async def handle_back(callback: CallbackQuery):
    from handlers.commands import start_cmd
    await start_cmd(callback.message)
    await callback.answer()

# Показываем товары
async def show_products(callback: CallbackQuery, cat_code: str, subcat: str):
    category_map = {
        "мягкая": "🛋 Мягкая мебель",
        "кухонная": "🍳 Кухонная мебель",
        "спальная": "🛏 Спальная мебель",
        "столы": "📚 Столы и стулья",
        "тумбы": "📺 Тумбы и комоды",
        "матрасы": "🛏 Матрасы",
        "шкафы": "🚪 Шкафы"
    }

    category_name = category_map.get(cat_code)
    categories = crud.get_categories()
    category = next((c for c in categories if c["name"] == category_name), None)
    if not category:
        await callback.message.answer("❌ Категория не найдена.")
        await callback.answer()
        return

    products = crud.get_products_by_category(category["id"], subcat)
    if not products:
        await callback.message.answer("⚠️ Товары пока не добавлены.")
        await callback.answer()
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{p['title']} — {p['price']}₽", callback_data=f"prod:{p['id']}")]
        for p in products
    ] + [[InlineKeyboardButton(text="⬅️ Назад", callback_data="назад")]])

    await callback.message.answer("📦 Товары:", reply_markup=kb)
    await callback.answer()

# Карточка товара
@router.callback_query(F.data.startswith("prod:"))
async def product_card(callback: CallbackQuery):
    prod_id = int(callback.data.split(":")[1])
    product = crud.get_product(prod_id)

    if not product:
        await callback.message.answer("❌ Товар не найден.")
        await callback.answer()
        return

    media = []
    for i in range(1, 5):
        img = product.get(f'image{i}')
        if img:
            media.append(InputMediaPhoto(media='https://www.bing.com/images/search?view=detailV2&ccid=aO7k18o4&id=FB1A3A6CB720D534B07F4D4130CFE240082862B4&thid=OIP.aO7k18o4aIbowjYfn4d-xAHaG2&mediaurl=https%3a%2f%2fe7.pngegg.com%2fpngimages%2f203%2f108%2fpng-clipart-cat-pixel-art-stardew-valley-cat-animals-black.png&cdnurl=https%3a%2f%2fth.bing.com%2fth%2fid%2fR.68eee4d7ca386886e8c2361f9f877ec4%3frik%3dtGIoCEDizzBBTQ%26pid%3dImgRaw%26r%3d0&exph=833&expw=900&q=pictures+150+x+150&FORM=IRPRST&ck=0DB17AE765DC7369433AA24BF504173D&selectedIndex=79&itb=0&ajaxhist=0&ajaxserp=0'))

    if media:
        if len(media) == 1:
            await callback.message.answer_photo(media[0].media)
        else:
            await callback.message.answer_media_group(media)

    text = (
        f"<b>{product['title']}</b>\n\n"
        f"{product.get('description', 'Нет описания')}\n\n"
        f"🌍 <b>Страна:</b> {product.get('country', '—')}\n"
        f"📏 <b>Размеры:</b> {product.get('size', '—')}\n"
        f"💰 <b>Цена:</b> {product.get('price')} ₽"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Задать вопрос", callback_data=f"chat:{prod_id}")],
        [InlineKeyboardButton(text="📞 Консультация", callback_data=f"consult:{prod_id}")],
        [InlineKeyboardButton(text="🛒 Оформить заказ", callback_data=f"bron:{prod_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="назад")]
    ])

    await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

# Заказ — FSM
@router.callback_query(F.data.startswith("bron:"))
async def start_bron(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
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
        ID_ADMIN,
        f"🆕 Новый заказ!\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"📦 Товар ID: {data['product_id']}\n"
        f"💬 Комментарий: {comment}"
    )

    await state