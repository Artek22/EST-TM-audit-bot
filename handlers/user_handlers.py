from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from utils.statesform import UserForm

from lexicon.lexicon import LEXICON_COMMANDS, LEXICON
from keyboards.keyboards import create_confirmation_keyboard

router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(f'{LEXICON_COMMANDS["/start"]}')
    await state.set_state(UserForm.GET_NAME)
    # await message.answer(text='___Пример форматированного текста___',
    #                      parse_mode='MarkdownV2')


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
    await message.answer(text=f'Тебя зовут {name} {surname}, все верно?',
                         reply_markup=create_confirmation_keyboard())
    await state.clear()


@router.callback_query(F.data == 'canceled')
async def process_canceled(callback: CallbackQuery):
    await callback.message.answer(text='Нажмите /start')
    print(callback.model_dump_json(indent=4, exclude_none=True))
    await callback.answer()


@router.callback_query(F.data == 'confirmed')
async def process_canceled(callback: CallbackQuery):
    # Todo: Сохраняем данные в базу
    print(callback.model_dump_json(indent=4, exclude_none=True))
    await callback.answer()
