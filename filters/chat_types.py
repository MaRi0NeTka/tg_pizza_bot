from typing import Any
from aiogram.filters import Filter #base filter class
from aiogram import types, Bot

"""Это специальный класс который проверяет допустима ли отравка ответов
    от полученый комманд из допустимых типов чатов.
    Чтобы комманды из user_privat не работали в группе или наоборот.
    Нужно передать обязательный параметр chat_types где перечисляются чаты куда можно отправлять ответы,
    например комманда из user_privat может работать в группе, если она перечислена в chat_types"""


class ChatFilterTypes(Filter):

    def __init__(self, chat_types:list[str]) -> None:
        self.chat_types_lst = chat_types

    async def __call__(self, message:types.Message, *args: Any, **kwds: Any) -> Any:
        return message.chat.type in self.chat_types_lst

class IsAdmin(Filter):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(self, message:types.Message, bot:Bot) -> bool:
        return message.from_user.id in bot.my_admins_lst
