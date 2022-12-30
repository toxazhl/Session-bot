import uuid

from aiogram.utils.markdown import hlink
from sqlalchemy import (
    func,
    Column,
    BigInteger,
    DateTime,
    String,
    LargeBinary,
    Integer,
    Boolean,
<<<<<<< HEAD
    ForeignKey,
=======
    ForeignKey
>>>>>>> bcda1cf483b29e0bb6f36d959f3abeb56afdbed0
)
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
    telegram_id = Column(BigInteger)
    valid = Column(Boolean)
    first_name = Column(String(64))
    last_name = Column(String(64))
    username = Column(String(32))
    phone = Column(String(16))
    filename = Column(String(256))
    creation_date = Column(DateTime(timezone=True), default=func.now())


class Proxy(Base):
    __tablename__ = "proxy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme = Column(String(16))
    host = Column(String(16))
    port = Column(Integer)
    login = Column(String(32))
    password = Column(String(32))
    uses = Column(Integer, server_default="0")

    def pyro_format(self) -> dict[str, int | str]:
        return dict(
            scheme=self.scheme,
            hostname=self.host,
            port=self.port,
            username=self.login,
            password=self.password,
        )
