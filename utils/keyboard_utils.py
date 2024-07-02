# solana-webwallet/utils/keyboard_utils.py

from typing import List, Tuple, Union

from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_keyboard(keyboard_data: List[Tuple[str, Union[str, WebAppInfo]]],
                           width: int = 1) -> InlineKeyboardMarkup:
    """
        Функция для создания инлайн-клавиатуры.

        Args:
            keyboard_data (List[Tuple[str, Union[str, WebAppInfo]]]): Список кортежей, содержащих текст и
            callback_data/WebAppInfo для каждой кнопки.
            width (int, optional): Ширина клавиатуры (количество кнопок в ряду). По умолчанию 1.

        Returns:
            InlineKeyboardMarkup: Объект инлайн-клавиатуры.
    """
    # Создаем объект InlineKeyboardBuilder для построения инлайн-клавиатуры
    kb_builder = InlineKeyboardBuilder()

    # Создаем пустой список для хранения кнопок
    buttons = []

    # Итерируемся по элементам списка keyboard_data
    for text, callback_data in keyboard_data:
        # Проверяем, является ли callback_data объектом WebAppInfo
        if isinstance(callback_data, WebAppInfo):
            # Если да, создаем кнопку с параметром web_app
            button = InlineKeyboardButton(text=text, web_app=callback_data)
        else:
            # Если нет, создаем кнопку с параметром callback_data
            button = InlineKeyboardButton(text=text, callback_data=callback_data)

        # Добавляем созданную кнопку в список buttons
        buttons.append(button)

    # Добавляем ряд кнопок в объект InlineKeyboardBuilder с указанной шириной
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры, построенный с помощью InlineKeyboardBuilder
    return kb_builder.as_markup()
