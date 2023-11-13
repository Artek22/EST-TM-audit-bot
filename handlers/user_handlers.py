import datetime as dt

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery, FSInputFile
from utils.statesform import FSMUserForm, FSMCompetitor

from est_audit_bot import bot
from config_data.config import load_config
from lexicon.lexicon import LEXICON_COMMANDS, LEXICON
from keyboards.keyboards import (create_confirmation_keyboard,
                                 create_activity_keyboard, promo_type_keyboard,
                                 promo_for_keyboard, skip_keyboard,
                                 admin_keyboard, approve_keyboard,
                                 download_keyboard)
from utils.db_commands import (register_user, register_competitor, select_user,
                               is_user_in_db, export_xls, ya_disk_upload)

from db.models import User, Competitor
from db.engine import session

router = Router()
config = load_config()


@router.message(Command(commands='help'))
async def process_cancel_command_state(message: Message):
    """Этот хэндлер будет срабатывать на команду "/help" в любых состояниях."""
    await message.answer(LEXICON_COMMANDS['/help'])


@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    """Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
    кроме состояния по умолчанию, и отключать машину состояний
    """
    await message.answer(LEXICON_COMMANDS['/cancel'])
    await state.clear()


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    """/Start. Начало анкетрование пользователя, ввод имени"""
    # Проверяем есть ли юзер в базе
    user = select_user(message.chat.id)

    if message.chat.id == config.boss_id:
        await message.answer(
            f'Приветствую, босс! Рад тебя видеть, босс!',
            reply_markup=download_keyboard())
    elif message.chat.id == config.tg_bot.admin_id:
        await message.answer(f'Приветствую, {user.name}',
                             reply_markup=admin_keyboard())
    elif is_user_in_db(message.chat.id):
        await message.answer(f'Приветствую, {user.name}',
                             reply_markup=create_activity_keyboard())
    else:
        await message.answer(LEXICON_COMMANDS['/start'])
        await state.set_state(FSMUserForm.get_name)


@router.callback_query(F.data == 'c_count')
async def process_count_forms(callback: CallbackQuery):
    """Подсчет количества анкет"""
    await callback.message.delete()
    count = session.query(Competitor).count()
    await callback.message.answer(text=f'Анкет: {count}\n',
                                  reply_markup=admin_keyboard())


@router.callback_query(F.data == 'all_users')
async def process_count_forms(callback: CallbackQuery):
    """Вывод всех пользователей"""
    users = session.query(User)
    users_list = 'Пользователи:\n'
    for u in users:
        users_list += f'•{u.name} {u.surname}\n'
    await callback.message.delete()
    await callback.message.answer(users_list, reply_markup=admin_keyboard())


@router.message(StateFilter(FSMUserForm.get_name), F.text.isalpha())
async def get_name(message: Message, state: FSMContext):
    """Ввод фамилии"""
    await state.update_data(name=message.text)
    await message.answer(LEXICON['surname'])
    await state.set_state(FSMUserForm.get_surname)


@router.message(StateFilter(FSMUserForm.get_name))
async def warning_not_name(message: Message):
    """Проверка, что пользователь ввел буквы в имени"""
    await message.answer(LEXICON['err_name'])


@router.message(StateFilter(FSMUserForm.get_surname), F.text.isalpha())
async def get_surname(message: Message, state: FSMContext):
    """Подтверждаем корректность введённых имени и фамилии"""
    await state.update_data(surname=message.text)
    context_data = await state.get_data()
    name = context_data['name']
    surname = context_data['surname']
    await message.answer(text=f'Вас зовут {name} {surname}, всё верно?',
                         reply_markup=create_confirmation_keyboard())


@router.message(StateFilter(FSMUserForm.get_surname))
async def warning_not_surname(message: Message):
    """Проверка, что пользователь ввел буквы в фамилии"""
    await message.answer(LEXICON['err_surname'])


@router.callback_query(F.data.in_(['refused', 'confirmed']))
async def process_survey_finished(callback: CallbackQuery, state: FSMContext):
    """Обработка подтверждения или отрицания пользователя на корректность
    имени и фамилии
    """
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


@router.callback_query(F.data == 'export')
async def export2excel(callback: CallbackQuery):
    """Экспорт БД в эксель-файл и заливка на Я.Диск"""
    await callback.message.delete()
    await callback.message.answer(LEXICON['loading'])
    await ya_disk_upload(callback)
    export_xls()
    date = dt.datetime.now().strftime("%d-%m-%y")
    file = FSInputFile(f'promo_audit{date}.xlsx')
    await callback.message.answer_document(document=file,
                                           caption='Загрузка завершена.',
                                           reply_markup=download_keyboard())


@router.callback_query(StateFilter(default_state), F.data == 'send_activity')
async def process_survey_start(callback: CallbackQuery, state: FSMContext):
    """Начало опроса активности конкурентов. Ввод клиента, который проводит
    промо.
    """
    await callback.message.delete()
    await callback.message.answer(LEXICON['client'])
    await state.set_state(FSMCompetitor.get_client)


# Сохраняем название клиента
@router.message(StateFilter(FSMCompetitor.get_client))
async def get_client(message: Message, state: FSMContext):
    """Ввод товарного направления"""
    await state.update_data(client=message.text)
    await message.answer(LEXICON['commodity_direction'])
    await state.set_state(FSMCompetitor.get_commodity_direction)


# Сохраняем товарное направление
@router.message(StateFilter(FSMCompetitor.get_commodity_direction))
async def get_commodity_direction(message: Message, state: FSMContext):
    """Ввод промоутируемого бренда"""
    await state.update_data(commodity_direction=message.text)
    await message.answer(LEXICON['brand']),
    await state.set_state(FSMCompetitor.get_brand)


# Сохраняем бренд
@router.message(StateFilter(FSMCompetitor.get_brand))
async def get_brand(message: Message, state: FSMContext):
    """Выбор на кого направлена акция"""
    await state.update_data(brand=message.text)
    await message.answer(LEXICON['promo_for'],
                         reply_markup=promo_for_keyboard()),
    await state.set_state(FSMCompetitor.get_promo_for)


# Сохраняем на кого направлена акция
@router.callback_query(StateFilter(FSMCompetitor.get_promo_for))
async def get_promo_for(callback: CallbackQuery, state: FSMContext):
    """Выбор типа акции"""
    await state.update_data(promo_for=callback.data)
    await callback.message.delete()
    await callback.message.answer(LEXICON['promo_type'],
                                  reply_markup=promo_type_keyboard()),
    await state.set_state(FSMCompetitor.get_promo_type)


# Сохраняем тип акции
@router.callback_query(StateFilter(FSMCompetitor.get_promo_type))
async def get_promo_type(callback: CallbackQuery, state: FSMContext):
    """Ввод размера бонуса"""
    await state.update_data(promo_type=callback.data)
    await callback.message.delete()
    await callback.message.answer(LEXICON['bonus'])
    await state.set_state(FSMCompetitor.get_bonus)


# Сохраняем бонус
@router.message(StateFilter(FSMCompetitor.get_bonus))
async def get_bonus(message: Message, state: FSMContext):
    """Ввод условия получения бонуса"""
    await state.update_data(bonus=message.text)
    await message.answer(LEXICON['condition']),
    await state.set_state(FSMCompetitor.get_condition)


# Сохраняем условие
@router.message(StateFilter(FSMCompetitor.get_condition))
async def get_condition(message: Message, state: FSMContext):
    """Получение фотографии акции"""
    await state.update_data(condition=message.text)
    await message.answer(LEXICON['photo']),
    await state.set_state(FSMCompetitor.get_photo)


# Сохраняем фото
@router.message(StateFilter(FSMCompetitor.get_photo), F.photo)
async def get_files_id(message: Message, state: FSMContext):
    """Получение комментария"""
    await state.update_data(files_id=message.photo[-1].file_id)
    await message.answer(LEXICON['comment'], reply_markup=skip_keyboard())
    await state.set_state(FSMCompetitor.get_comment)


@router.message(StateFilter(FSMCompetitor.get_photo))
async def get_files_id_not_photo(message: Message):
    """Получение фотографии акции"""
    await message.answer('Это не похоже на фото.')


# Сохраняем комментарий
@router.message(StateFilter(FSMCompetitor.get_comment), F.text)
async def get_comment(message: Message, state: FSMContext):
    """Подтверждение акции с комментарием"""
    await state.update_data(comment=message.text)
    await state.update_data(user_id=message.chat.id)
    await state.set_state(FSMCompetitor.confirm)
    data = await state.get_data()
    await message.answer(LEXICON['confirm'])
    info = (
        f'Клиент: {data["client"]}\n'
        f'Товарное направление: {data["commodity_direction"]}\n'
        f'Бренд: {data["brand"]}\n'
        f'Для кого акция: {data["promo_for"]}\n'
        f'Тип промо: {data["promo_type"]}\n'
        f'Какой бонус: {data["bonus"]}\n'
        f'Условие получения: {data["condition"]}\n'
        f'Комментарий: {data["comment"]}\n'
    )
    image = data['files_id']
    await message.answer_photo(
        photo=image,
        caption=info,
        reply_markup=approve_keyboard())


# Сохраняем пустой комментарий
@router.callback_query(StateFilter(FSMCompetitor.get_comment), F.data == 'skip')
async def get_no_comment(callback: CallbackQuery, state: FSMContext):
    """Подтверждение акции без комментария"""
    await state.update_data(comment='')
    await state.update_data(user_id=callback.message.chat.id)
    await state.set_state(FSMCompetitor.confirm)
    data = await state.get_data()
    await callback.message.answer(LEXICON['confirm'])
    info = (
        f'Клиент: {data["client"]}\n'
        f'Товарное направление: {data["commodity_direction"]}\n'
        f'Бренд: {data["brand"]}\n'
        f'Для кого акция: {data["promo_for"]}\n'
        f'Тип промо: {data["promo_type"]}\n'
        f'Какой бонус: {data["bonus"]}\n'
        f'Условие получения: {data["condition"]}\n'
        f'Комментарий: {data["comment"]}\n'
    )
    image = data['files_id']
    await callback.message.answer_photo(
        photo=image,
        caption=info,
        reply_markup=approve_keyboard())


@router.callback_query(FSMCompetitor.confirm, F.data == 'approved')
async def process_saving_task_to_db(callback: CallbackQuery, state: FSMContext):
    """Подтверждение акции и высылка акции боссу"""
    await callback.message.delete()
    data = await state.get_data()
    get_user = session.get(User, callback.message.chat.id)
    author = f'{get_user.name} {get_user.surname}'
    info = (
        f'Автор: {author}\n'
        f'══════ ≽^•⩊•^≼ ══════\n'
        f'Клиент: {data["client"]}\n'
        f'Товарное направление: {data["commodity_direction"]}\n'
        f'Бренд: {data["brand"]}\n'
        f'Для кого акция: {data["promo_for"]}\n'
        f'Тип промо: {data["promo_type"]}\n'
        f'Какой бонус: {data["bonus"]}\n'
        f'Условие получения: {data["condition"]}\n'
        f'Комментарий: {data["comment"]}\n'
    )
    image = data['files_id']
    # Сохраняем акцию
    await callback.message.answer(text='Сохраняем...')
    register_competitor(data)
    await state.clear()
    # Высылаем акцию боссу
    await bot.send_photo(chat_id=config.boss_id, photo=image,
                         caption=f'Привет, новая акция:\n{info}')
    await bot.session.close()
    if callback.message.chat.id == config.boss_id:
        await callback.message.answer(LEXICON['finish'],
                                      reply_markup=download_keyboard())
    elif is_user_in_db(callback.message.chat.id):
        await callback.message.answer(LEXICON['finish'],
                                      reply_markup=create_activity_keyboard())


@router.callback_query(FSMCompetitor.confirm, F.data == 'rejected')
async def process_saving_task_to_db(callback: CallbackQuery, state: FSMContext):
    """Отмена акции"""
    await callback.message.delete()
    await callback.message.answer('Попробуем еще раз?',
                                  reply_markup=create_activity_keyboard())
    await state.clear()
