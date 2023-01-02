from aiogram.fsm.state import State, StatesGroup


class UploadStates(StatesGroup):
    upload = State()
    manual_auth_key = State()
    manual_dc_id = State()
    manual_user_id = State()


class LoginStates(StatesGroup):
    phone_number = State()
    phone_confirm = State()
    phone_code = State()
    password = State()


class ProfileStates(StatesGroup):
    refill_amount = State()
