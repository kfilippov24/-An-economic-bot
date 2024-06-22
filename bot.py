import asyncio
from contextlib import suppress

from aiogram import Router, Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode

from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticDatabase as MDB
from pymongo.errors import DuplicateKeyError

from callbacks import navigation, bank_loans_act

from keyboards.builders import inline_builder

from middlewares.throttling import ThrottlingMiddleware

from config_reader import config

router = Router()


@router.message(CommandStart())
@router.callback_query(F.data == "main_page")
async def start(message: Message | CallbackQuery, db: MDB) -> None:
    with suppress(DuplicateKeyError):
        await db.users.insert_one(
            dict(
                _id=message.from_user.id,
                balance=100,
                bank={
                    "currency": [0, 0, 0],
                    "loans": {
                        "total_amount": 0,
                        "repaid": {"amount": 0, "when": []},
                        "when": {"start": "", "end": ""}
                    },
                    "deposit": {"total_amount": 0, "when": ""}
                },
                actives={"total_amount": 0, "items": []},
                passives={"total_amount": 0, "items": []},
                businesses={"total_amount": 0, "items": []}
            )
        )

    pattern = dict(
        text="Let's get down business!",
        reply_markup=inline_builder(
            ["👤 Профиль", "🏦 Банк", "🏙 Рынки", "💸 Бизенс"],
            ["profile", "bank", "markets", "business"]
        )
    )

    if isinstance(message, CallbackQuery):
        await message.message.edit_text(**pattern)
        await message.answer()
    else:
        await message.answer(**pattern)


async def main() -> None:
    bot = Bot(config.BOT_TOKEN.get_secret_value(), parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    cluster = AsyncIOMotorClient(host="localhost", port=27017)
    db = cluster.ecodb

    dp.message.middleware(ThrottlingMiddleware())

    dp.include_routers(
        router,
        navigation.router,
        bank_loans_act.router
    )

    await bot.delete_webhook(True)
    await dp.start_polling(bot, db=db)


if __name__ == "__main__":
    asyncio.run(main())