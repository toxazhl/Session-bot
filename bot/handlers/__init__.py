from aiogram import Router


def setup_routers() -> Router:
    from . import registration, main_menu

    router = Router()
    router.include_router(registration.router)
    router.include_router(main_menu.router)

    return router
