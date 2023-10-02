from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Функция, генерирующая клавиатуру для подтверждения введенных данных
def create_confirmation_keyboard():
    # Создаем объект инлайн-клавиатуры
    confirmation_keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    confirmation_keyboard.row(InlineKeyboardButton(text='Подтвердить',
                                                   callback_data='confirmed'),
                              InlineKeyboardButton(text='Заново',
                                                   callback_data='refused'),
                              width=2)
    return confirmation_keyboard.as_markup()


def create_activity_keyboard():
    activity_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Выслать активность конкурентов',
        callback_data='send_activity')
    activity_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[activity_button]])
    return activity_keyboard


def promo_for_keyboard():
    promo_for: InlineKeyboardBuilder = InlineKeyboardBuilder()
    promo_for.row(InlineKeyboardButton(text='🧍ТП',
                                       callback_data='tp'),
                  InlineKeyboardButton(text='🧍СВ',
                                       callback_data='sv'),
                  InlineKeyboardButton(text='🧍ЛПР',
                                       callback_data='lpr'),
                  InlineKeyboardButton(text='🧍ТТ',
                                       callback_data='tt'),
                  InlineKeyboardButton(text='🧍КП',
                                       callback_data='kp'),
                  width=3)
    return promo_for.as_markup()


def promo_type_keyboard():
    promo_keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    promo_keyboard.row(InlineKeyboardButton(text='⬇️Скидка',
                                            callback_data='discount'),
                       InlineKeyboardButton(text='✨Бонус',
                                            callback_data='bonus'),
                       InlineKeyboardButton(text='🎁Подарок за покупку',
                                            callback_data='gift'),
                       width=2)
    return promo_keyboard.as_markup()


def approve_keyboard():
    approve_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Подтвердить', callback_data='approved')
    reject_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Отменить', callback_data='rejected')
    ok_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[approve_button], [reject_button]])
    return ok_keyboard


def download_keyboard():
    kb_builder = InlineKeyboardBuilder()
    activity_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Выслать активность конкурентов',
        callback_data='send_activity')
    download_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Экспорт БД в Excel', callback_data='export')
    kb_builder.row(activity_button, download_button, width=1)
    return kb_builder.as_markup()


def skip_keyboard():
    skip_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Пропустить',
        callback_data='skip')
    skip1_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
        inline_keyboard=[[skip_button]])
    return skip1_keyboard
