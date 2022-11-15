from aiogram.fsm.state import State, StatesGroup


class UploadStates(StatesGroup):
    upload_pyrogram = State()
    upload_telethon = State()
    upload_tdata = State()
