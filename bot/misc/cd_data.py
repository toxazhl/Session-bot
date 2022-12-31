from uuid import UUID

from aiogram.filters.callback_data import CallbackData


class SessionCb(CallbackData, prefix="sa"):
    session_id: UUID
    action: str
