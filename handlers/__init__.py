from .commands import router as commands_router
from .mebele_bro import router as mebele_bro_router
from .admin_commands import router as admin_commands_router
from .admin_obrabotka import router as admin_obrabotka_router
from .admin import router as admin_router

from aiogram import Router

router = Router()
router.include_router(commands_router)
router.include_router(mebele_bro_router)
router.include_router(admin_commands_router)
router.include_router(admin_obrabotka_router)
router.include_router(admin_router)