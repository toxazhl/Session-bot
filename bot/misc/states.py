from aiogram.fsm.state import State, StatesGroup


class UploadStates(StatesGroup):
    pyrogram = State()
    telethon = State()
    tdata = State()
    manual_auth_key = State()
    manual_dc_id = State()
    manual_user_id = State()
<<<<<<< HEAD


class LoginStates(StatesGroup):
    phone_number = State()
    phone_confirm = State()
    phone_code = State()
    password = State()
    
=======
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
