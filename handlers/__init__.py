from aiogram import Router
from .commands import router as commands_router
from .mebele_bro import router as mebele_bro_router
# from .categories import router as category_router

router = Router()
router.include_router(commands_router)
router.include_router(mebele_bro_router)
# router.include_router(category_router)