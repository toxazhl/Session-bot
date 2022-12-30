from pyrogram.client import Client


class AuthStorage:
    data: dict[int, Client] = {}

    @classmethod
    def get(cls, key: int) -> Client:
        return cls.data.get(key)
    
    @classmethod
    def set(cls, key, item):
        cls.data[key] = item
    
    @classmethod
    def _del(cls, key: int):
        cls.data.pop(key)
