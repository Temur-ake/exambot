from aiogram import Bot
from aiogram.filters import Filter
from aiogram.types import Message

from cons import ADMIN_ID


class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_types


class IsAdmin(Filter):
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __call__(self, message: Message, bot: Bot) -> bool:
        return message.from_user.id in ADMIN_LIST
