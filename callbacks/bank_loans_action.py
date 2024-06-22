from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

from motor.core import AgnosticDatabase as MDB
import pendulum

from filters.is_digit import IsDigit

from keyboards.builders import inline_builder
from utils.states import TakeLoanForm

router = Router()


@router.callback_query(F.data == "credit")
async def show_loans_act(query: CallbackQuery, state: FSMContext, db: MDB) -> None:
    user = await db.users.find_one(dict(_id=query.from_user.id))

    if user['bank']['loans']['when']['start']:
        await query.message.edit_text(
            f"Sorry, you have a loan -> {user['bank']['loans']['total_amount']}",
            reply_markup=inline_builder("⬅ Back", "bank")
        )
    else:
        await state.set_state(TakeLoanForm.term)
        await query.message.answer("For how long?")
    await query.answer()


@router.message(TakeLoanForm.term, IsDigit())
async def take_loan_form_term(message: Message, state: FSMContext) -> None:
    if int(message.text) <= 0 or int(message.text) > 10:
        await message.answer("From 1 to 10")
    else:
        await state.update_data(term=message.text)
        await state.set_state(TakeLoanForm.amount)
        await message.answer("For how much?")


@router.message(TakeLoanForm.amount, IsDigit())
async def take_loan_form_amount(message: Message, state: FSMContext, db: MDB) -> None:
    amount = int(message.text)

    if amount <= 0 or amount > 1000:
        await message.answer("From 0 to 1000")
    else:
        data = await state.get_data()

        current_datetime = pendulum.now("UTC")
        end_datetime = current_datetime.add(int(data["term"]))

        await state.clear()
        await message.answer(
            "You have successfully aplied for loan",
            reply_markup=inline_builder("⬅ Back", "bank")
        )

        await db.users.update_one(
            dict(_id=message.from_user.id),
            {
                "$inc": {"balance": amount, "bank.loans.total_amount": amount * (12.5 / 100)},
                "$set": {
                    "bank.loans.when.start": current_datetime,
                    "bank.loans.when.end": end_datetime
                }
            }
        )


@router.message(TakeLoanForm.term)
async def incorrect_tlf_term(message: Message, state: FSMContext) -> None:
    await message.answer("Enter a correct data, please!")


@router.message(TakeLoanForm.amount)
async def incorrect_tlf_term(message: Message, state: FSMContext) -> None:
    await message.answer("Enter a correct data, please!")