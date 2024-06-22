from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsDigit(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        if message.text.isnumeric() or (message.text.count(".") == 1 and message.text.replace(".", "").isnumeric()):
            return True
        return False