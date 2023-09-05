from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from utils.statesform import FSMUserForm, FSMCompetitor

from lexicon.lexicon import LEXICON_COMMANDS, LEXICON
from keyboards.keyboards import create_confirmation_keyboard

router = Router()
# Создаем "базу данных" пользователей
user_dict = {}


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Чтобы снова перейти к заполнению анкеты - '
                              'отправьте команду /start')
    await state.clear()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    await message.answer(f'{LEXICON_COMMANDS["/start"]}')
    await state.set_state(FSMUserForm.get_name)


@router.message(StateFilter(FSMUserForm.get_name), F.text.isalpha())
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f'{LEXICON["surname"]}')
    await state.set_state(FSMUserForm.get_surname)


@router.message(StateFilter(FSMUserForm.get_name))
async def warning_not_name(message: Message):
    await message.answer(text='То, что вы отправили не похоже на имя.\n\n'
                              'Пожалуйста, введите ваше имя.\n\n'
                              'Если вы хотите прервать заполнение анкеты - '
                              'отправьте команду /cancel')


@router.message(StateFilter(FSMUserForm.get_surname), F.text.isalpha())
async def get_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    context_data = await state.get_data()
    name = context_data['name']
    surname = context_data['surname']
    await message.answer(text=f'Тебя зовут {name} {surname}, все верно?',
                         reply_markup=create_confirmation_keyboard())


@router.message(StateFilter(FSMUserForm.get_surname))
async def warning_not_surname(message: Message):
    await message.answer(text='То, что вы отправили не похоже на фамилию.\n\n'
                              'Пожалуйста, введите вашу фамилию.\n\n'
                              'Если вы хотите прервать заполнение анкеты - '
                              'отправьте команду /cancel')


@router.callback_query(F.data.in_(['refused', 'confirmed']))
async def process_survey_finished(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'refused':
        await callback.message.answer(f'{LEXICON_COMMANDS["/start"]}')
        await callback.message.delete()
        await state.set_state(FSMUserForm.get_name)
    else:
        user_dict[callback.from_user.id] = await state.get_data()
        with open('db/db.txt', 'w') as file:
            for key, value in user_dict.items():
                file.write(f'{key}: {value}')
        await state.clear()
        await callback.message.edit_text(text=f'Спасибо! Ваши данные сохранены.')

# Начинаем опрос пользователя
