from aiogram.fsm.state import State, StatesGroup


class RegStates(StatesGroup):
    phone_number = State()
