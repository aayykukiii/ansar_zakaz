from aiogram.fsm.state import StatesGroup, State

class AddCategoryFSM(StatesGroup):
    waiting_for_name = State()

class AddProductFSM(StatesGroup):
    waiting_for_title = State()
    waiting_for_category = State()
    waiting_for_subcategory = State()
    waiting_for_country = State()
    waiting_for_type = State()
    waiting_for_price = State()
    waiting_for_size = State()
    waiting_for_description = State()
    waiting_for_images = State()
