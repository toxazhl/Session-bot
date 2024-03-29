from aiogram import Router


def setup_routers() -> Router:
    from . import upload, menu, download, login

    router = Router()
    router.include_router(upload.router)
    router.include_router(login.router)
    router.include_router(menu.router)
    router.include_router(download.router)

    return router
