from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from utils.statesform import UserForm

from lexicon.lexicon import LEXICON_COMMANDS, LEXICON

router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(f'{LEXICON_COMMANDS["/start"]}')
    await state.set_state(UserForm.GET_NAME)


@router.message(UserForm.GET_NAME)
async def get_name(message: Message, state: FSMContext):
    await message.answer(f'{LEXICON["surname"]}')
    await state.update_data(name=message.text)
    await state.set_state(UserForm.GET_SURNAME)


@router.message(UserForm.GET_SURNAME)
async def get_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    context_data = await state.get_data()
    name = context_data['name']
    surname = context_data['surname']
    await message.answer(f'Тебя зовут {name} {surname}')
    await state.clear()
