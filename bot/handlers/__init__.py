from aiogram import Router


def setup_routers() -> Router:
    from . import sessions, main_menu

    router = Router()
    router.include_router(main_menu.router)
    router.include_router(sessions.setup_routers())

    return router
