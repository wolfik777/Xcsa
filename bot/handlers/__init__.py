"""
Handlers package
"""
from aiogram import Router
from .start import router as start_router
from .download import router as download_router
from .referral import router as referral_router
from .tools import router as tools_router
from .admin import router as admin_router


def get_routers() -> list[Router]:
    """Get all routers"""
    return [
        admin_router,     # Админ-панель должна быть первой
        start_router,
        referral_router,
        tools_router,
        download_router,  # Должен быть последним, так как ловит все URL
    ]

