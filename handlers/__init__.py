from .client_panel import router as client_panel_router
from .client_obrabotka import router as client_obrabotka_router
from .admin_panel import router as admin_panel_router
from .admin_obrabotka import router as admin_obrabotka_router

from aiogram import Router

router = Router()
router.include_router(client_panel_router)
router.include_router(client_obrabotka_router)
router.include_router(admin_panel_router)
router.include_router(admin_obrabotka_router)