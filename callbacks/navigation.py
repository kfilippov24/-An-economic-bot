from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hcode

from motor.core import AgnosticDatabase as MDB

from keyboards.builders import inline_builder

router = Router()


@router.callback_query(F.data == "profile")
async def show_profile(query: CallbackQuery, db: MDB) -> None:
    user = await db.users.find_one(dict(_id=query.from_user.id))

    await query.message.edit_text(
        f"ID: {hcode(query.from_user.id)}\n\n"
        f"💸 Balance: {hcode(user['balance'])} $\n"
        f"📈 Actives: {hcode(user['actives']['total_amount'])} $\n"
        f"📉 Passives: {hcode(user['passives']['total_amount'])} $\n"
        f"💲 Businesses: {hcode(user['businesses']['total_amount'])} $\n",
        reply_markup=inline_builder("⬅ Back", "main_page")
    )
    await query.answer()


@router.callback_query(F.data == "bank")
async def show_bank(query: CallbackQuery, db: MDB) -> None:
    user = await db.users.find_one(dict(_id=query.from_user.id))

    pattern = dict(
        text=
            f"Currencies: {hcode(user['bank']['currency'][0])} 💵 |"
            f"{hcode(user['bank']['currency'][1])} 💶 | "
            f"{hcode(user['bank']['currency'][2])} 💷\n"
            f"Loan: {hcode(user['bank']['loans']['total_amount'])} $\n"
            f"Deposit: {hcode(user['bank']['deposit']['total_amount'])} $",
        reply_markup=inline_builder(
            ["Кредит", "Депозит", "Back"],
            ["credit", "deposit", "main_page"]
        )
    )

    await query.message.edit_text(**pattern)
    await query.answer()