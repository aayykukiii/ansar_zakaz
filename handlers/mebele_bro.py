from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from database import crud
from handlers.commands import start_cmd
import re
from states.mebel_bron import BronForm

router = Router()

@router.callback_query(F.data.startswith("cat:"))
async def handle_category(callback: CallbackQuery, state: FSMContext):
    code = callback.data.split(":", 1)[1]

    subcats_map = {
        "spalnaya": ["ru", "tr"],
        "kuhonnaya": ["pryamaya", "uglovaya"],
        "myagkaya": ["ru", "tr"],
        "krovati": ["ru", "tr"],
    }
    categories_without_subcats = {"stoly_stulya", "tumby_komody", "matrasy", "shkafy"}

    if code == "about":
        await callback.message.answer(
            "📞 Контакты:\n"
            "🏢 Компания по продаже мебели\n"
            "📍 Адрес компании\n"
            "📱 +7 (995) 800‑89‑95"
        )
        await callback.answer()
        return

    if code in categories_without_subcats:
        cat = crud.get_category_by_code(code)
        if cat:
            await show_products(callback, cat.id, subcat=None)
        else:
            await callback.message.answer("❌ Категория не найдена.")
        await callback.answer()
        return

    if code not in subcats_map:
        await callback.message.answer("❌ Неизвестная категория.")
        await callback.answer()
        return

    buttons = []
    for sub in subcats_map[code]:
        if code in ("spalnaya", "myagkaya", "krovati"):
            txt = "🇷🇺 Российская" if sub == "ru" else "🇹🇷 Турецкая"
        elif code == "kuhonnaya":
            txt = "📐 Прямая" if sub == "pryamaya" else "🔽 Угловая"
        else:
            txt = sub
        cb = f"subcat:{code}:{sub}"
        buttons.append([InlineKeyboardButton(text=txt, callback_data=cb)])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")])

    await callback.message.answer(f"Категория: {code.replace('_', ' ').capitalize()}\nВыберите подкатегорию:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()

@router.callback_query(F.data.startswith("subcat:"))
async def handle_subcat(callback: CallbackQuery, state: FSMContext):
    _, cat_code, sub_code = callback.data.split(":", 2)
    cat = crud.get_category_by_code(cat_code)
    if not cat:
        await callback.message.answer("❌ Категория не найдена.")
        await callback.answer()
        return
    await show_products(callback, cat.id, subcat=sub_code)

@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    await start_cmd(callback.message)
    await callback.answer()

async def show_products(callback: CallbackQuery, category_id: int, subcat: str = None):
    products = crud.get_products_by_category(category_id, subcat=subcat)
    if not products:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")]
        ])
        await callback.message.answer("⚠️ Товары пока не добавлены.", reply_markup=kb)
        await callback.answer()
        return

    buttons = [[InlineKeyboardButton(text=f"{p.title} — {p.price}₽", callback_data=f"prod:{p.id}")] for p in products]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except:
        await callback.message.answer("Выберите товар:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("prod:"))
async def product_card(callback: CallbackQuery, state: FSMContext):
    prod_id = int(callback.data.split(":", 1)[1])
    product = crud.get_product(prod_id)
    if not product:
        await callback.message.answer('❌ Товар не найден')
        await callback.answer()
        return

    media = []
    for img in (product.image1, product.image2, product.image3, product.image4):
        if img:
            media.append(InputMediaPhoto(media=img))
    if media:
        if len(media) == 1:
            await callback.message.answer_photo(media[0].media)
        else:
            await callback.message.answer_media_group(media)

    text = (
        f"<b>{product.title}</b>\n\n"
        f"{product.description or 'Нет описания'}\n\n"
        f"🌍 <b>Страна:</b> {product.country or '—'}\n"
        f"📏 <b>Размер:</b> {product.size or '—'}\n"
        f"💰 <b>Цена:</b> {product.price or '—'} ₽"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Задать вопрос", callback_data=f"chat:{product.id}")],
        [InlineKeyboardButton(text="📞 Консультация", callback_data=f"consult:{product.id}")],
        [InlineKeyboardButton(text="🛒 Оформить заказ", callback_data=f"bron:{product.id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start")]
    ])
    await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("bron:"))
async def start_bron(callback: CallbackQuery, state: FSMContext):
    prod_id = int(callback.data.split(":", 1)[1])
    await state.update_data(product_id=prod_id)
    await state.set_state(BronForm.waiting_for_name)
    await callback.message.answer("Введите ваше имя:")
    await callback.answer()

# FSM обработка броней:

@router.message(BronForm.waiting_for_name)
async def bron_name(message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(BronForm.waiting_for_phone)
    await message.answer("Введите телефон (например +79991234567):")

@router.message(BronForm.waiting_for_phone)
async def bron_phone(message, state: FSMContext):
    phone = message.text.strip()
    if not re.match(r"^\+7\d{10}$", phone):
        await message.answer("⚠️ Неверный формат. Попробуйте снова:")
        return
    await state.update_data(phone=phone)
    await state.set_state(BronForm.waiting_for_comment)
    await message.answer("Комментарий (или '-' если без):")

@router.message(BronForm.waiting_for_comment)
async def bron_comment(message, state: FSMContext):
    data = await state.get_data()
    comment = message.text if message.text != "-" else ""
    crud.create_order(
        user_id=message.from_user.id,
        name=data["name"],
        phone=data["phone"],
        product_id=data["product_id"],
        comment=comment
    )
    product = crud.get_product(data["product_id"])
    await message.answer(f"✅ Заказ оформлен: <b>{product.title}</b>", parse_mode="HTML")
    # уведомление админу
    from config import ID_ADMIN
    await message.bot.send_message(
        chat_id=ID_ADMIN,
        text=(
            f"🆕 Новый заказ\n"
            f"Имя: {data['name']}\n"
            f"Телефон: {data['phone']}\n"
            f"Товар: {product.title}\n"
            f"Комментарий: {comment or '—'}"
        )
    )
    await state.clear()
