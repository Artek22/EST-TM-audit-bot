from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Функция, генерирующая клавиатуру для подтверждения введенных данных
def create_confirmation_keyboard():
    # Создаем объект инлайн-клавиатуры
    confirmation_keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    confirmation_keyboard.row(InlineKeyboardButton(text='Подтвердить',
                                                   callback_data='confirmed'),
                              InlineKeyboardButton(text='Заново',
                                                   callback_data='canceled'),
                              width=2)
    return confirmation_keyboard.as_markup()
