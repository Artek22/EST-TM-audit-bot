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


def promo_type_keyboard():
    promo_keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    promo_keyboard.row(InlineKeyboardButton(text='⬇️Скидка на полке',
                                            callback_data='discount'),
                       InlineKeyboardButton(text='🎁Подарок за покупку',
                                            callback_data='gift'),
                       InlineKeyboardButton(text='✨Бонус ТП',
                                            callback_data='bonus_tp'),
                       InlineKeyboardButton(text='✨Бонус ЛПР',
                                            callback_data='bonus_lpr'),
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
