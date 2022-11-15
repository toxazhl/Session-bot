import uuid

from aiogram.utils.markdown import hlink
from sqlalchemy import func, Column, BigInteger, DateTime, String, LargeBinary, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from bot.core.db.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True)
    phone_number = Column(String(16))
    creation_date = Column(DateTime(timezone=True), default=func.now())

    def __repr__(self) -> str:
        return f"User(id={self.id}, phone_number={self.phone_number})"

    def hyperlink(self, name: str) -> str:
        return hlink(name, f"tg://user?id={self.id}")


class Session(Base):
    __tablename__ = "session"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(BigInteger, ForeignKey("user.id"))
    dc_id = Column(Integer)
    auth_key = Column(LargeBinary)
    api_id = Column(Integer)
    server_address = Column(String(255))
    port = Column(Integer)
    telegram_id = Column(BigInteger)
    test_mode = Column(Boolean)
    is_bot = Column(Boolean)
    valid = Column(Boolean)
    creation_date = Column(DateTime(timezone=True), default=func.now())
