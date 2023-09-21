from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from utils.statesform import FSMUserForm, FSMCompetitor

from lexicon.lexicon import LEXICON_COMMANDS, LEXICON
from keyboards.keyboards import (create_confirmation_keyboard,
                                 create_activity_keyboard, promo_type_keyboard)
from utils.db_commands import (register_user, register_competitor, select_user,
                               is_user_in_db)

router = Router()


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(LEXICON_COMMANDS['/cancel'])
    await state.clear()


# Этот хэндлер срабатывает на команду /start
# Ввод имени
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    # Проверяем есть ли юзер в базе
    user = select_user(message.chat.id)
    if is_user_in_db(message.chat.id):
        await state.clear()
        await message.answer(f'Добро пожаловать, {user.name}',
                             reply_markup=create_activity_keyboard())
    else:
        await message.answer(LEXICON_COMMANDS['/start'])
        await state.set_state(FSMUserForm.get_name)


# Ввод фамилии
@router.message(StateFilter(FSMUserForm.get_name), F.text.isalpha())
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(LEXICON['surname'])
    await state.set_state(FSMUserForm.get_surname)


@router.message(StateFilter(FSMUserForm.get_name))
async def warning_not_name(message: Message):
    await message.answer(LEXICON['err_name'])


# Подтверждение ввода данных
@router.message(StateFilter(FSMUserForm.get_surname), F.text.isalpha())
async def get_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    context_data = await state.get_data()
    name = context_data['name']
    surname = context_data['surname']
    await message.answer(text=f'Вас зовут {name} {surname}, все верно?',
                         reply_markup=create_confirmation_keyboard())


@router.message(StateFilter(FSMUserForm.get_surname))
async def warning_not_surname(message: Message):
    await message.answer(LEXICON['err_surname'])


@router.callback_query(F.data.in_(['refused', 'confirmed']))
async def process_survey_finished(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'refused':
        await callback.message.answer(LEXICON_COMMANDS["/start"])
        await callback.message.delete()
        await state.set_state(FSMUserForm.get_name)
    else:
        await state.update_data(id=int(callback.message.chat.id))
        user_data = await state.get_data()
        register_user(user_data)
        await state.clear()
        await callback.message.edit_text(LEXICON['confirmed'],
                                         reply_markup=create_activity_keyboard())


# Начинаем опрос пользователя
@router.callback_query(StateFilter(default_state), F.data == 'send_activity')
async def process_survey_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(LEXICON['company_name'])
    await state.set_state(FSMCompetitor.get_company_name)


# Сохраняем название компании
@router.message(StateFilter(FSMCompetitor.get_company_name))
async def get_company_name(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await message.answer(LEXICON['brand']),
    await state.set_state(FSMCompetitor.get_brand)


# Сохраняем бренд
@router.message(StateFilter(FSMCompetitor.get_brand))
async def get_brand(message: Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer(LEXICON['promo_type'],
                         reply_markup=promo_type_keyboard()),
    await state.set_state(FSMCompetitor.get_promo_type)


# Сохраняем тип акции
@router.callback_query(StateFilter(FSMCompetitor.get_promo_type))
async def get_promo_type(callback: CallbackQuery, state: FSMContext):
    await state.update_data(promo_type=callback.data)
    await callback.message.delete()
    await callback.message.answer(LEXICON['bonus'])
    await state.set_state(FSMCompetitor.get_bonus)


# Сохраняем бонус
@router.message(StateFilter(FSMCompetitor.get_bonus))
async def get_bonus(message: Message, state: FSMContext):
    await state.update_data(bonus=message.text)
    await message.answer(LEXICON['condition']),
    await state.set_state(FSMCompetitor.get_condition)


# Сохраняем условие
@router.message(StateFilter(FSMCompetitor.get_condition))
async def get_condition(message: Message, state: FSMContext):
    await state.update_data(condition=message.text)
    await message.answer(LEXICON['photo']),
    await state.set_state(FSMCompetitor.get_photo)


@router.message(StateFilter(FSMCompetitor.get_photo))
async def get_files_id(message: Message, state: FSMContext):
    await state.update_data(files_id=message.photo[0].file_id)
    await state.update_data(user_id=message.chat.id)
    data = await state.get_data()
    register_competitor(data)
    await message.answer(LEXICON['finish'],
                         reply_markup=create_activity_keyboard()),
    await state.clear()
