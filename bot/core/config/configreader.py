from pydantic import BaseModel, BaseSettings, PostgresDsn, RedisDsn


class Bot(BaseModel):
    token: str
    use_redis: bool


class Path(BaseModel):
    bot: str


class Web(BaseModel):
    enable_webhook: bool
    host: None | str = "localhost"
    port: None | int = 8000
    domain: None | str
    path: Path


class Config(BaseSettings):
    bot: Bot
    web: Web
    postgres_dsn: PostgresDsn
    redis_dsn: None | RedisDsn

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
