from aiogram import Router


def setup_routers() -> Router:
    from . import errors, main_menu, profile, sessions

    router = Router()
    router.include_router(main_menu.router)
    router.include_router(profile.router)
    router.include_router(sessions.setup_routers())
    router.include_router(errors.router)

    return router
