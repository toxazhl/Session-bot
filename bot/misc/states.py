from aiogram.fsm.state import State, StatesGroup


class UploadStates(StatesGroup):
    pyrogram = State()
    telethon = State()
    tdata = State()
    manual_auth_key = State()
    manual_dc_id = State()
    manual_user_id = State()
