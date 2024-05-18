# solana_wallet_telegram_bot/keyboards/main_keyboard.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.lexicon_en import LEXICON


# Функция для создания инлайн-кнопки
def create_button(text: str, callback_data: str) -> InlineKeyboardButton:
    """
        Creates an inline button.

        :param text: The text of the button.
        :param callback_data: The callback data for the button.
        :return: The created inline button.
    """
    return InlineKeyboardButton(text=text, callback_data=callback_data)


# Функция для создания клавиатуры с кнопками
def create_keyboard(data: list) -> InlineKeyboardMarkup:
    """
        Creates a keyboard with inline buttons based on the provided data.

        Args:
            data (list): A list of tuples, each containing the button text and callback data.

        Returns:
            InlineKeyboardMarkup: The created keyboard with inline buttons.
    """
    buttons = []                                          # Создание пустого списка для кнопок
    for text, callback_data in data:                      # Итерация по данным для кнопок
        button = create_button(text, callback_data)       # Создание инлайн-кнопки
        buttons.append([button])                          # Добавление кнопки в список кнопок
    return InlineKeyboardMarkup(inline_keyboard=buttons)  # Создание клавиатуры из списка кнопок


# Создание данных для кнопок с использованием лексикона
button_data = [
    # Текст кнопки и данные обратного вызова для создания кошелька
    (LEXICON["create_wallet"], "callback_button_create_wallet"),
    # Текст кнопки и данные обратного вызова для создания кошелька из Seed фразы
    (LEXICON["create_wallet_from_seed"], "callback_button_create_wallet_from_seed"),
    # Текст кнопки и данные обратного вызова для подключения кошелька
    (LEXICON["connect_wallet"], "callback_button_connect_wallet"),
    # Текст кнопки и данные обратного вызова для проверки баланса
    (LEXICON["balance"], "callback_button_balance"),
    # Текст кнопки и данные обратного вызова для передачи токенов
    (LEXICON["token_transfer"], "callback_button_transfer"),
    # Текст кнопки и данные обратного вызова для просмотра транзакций
    (LEXICON["transaction"], "callback_button_transaction"),
    # Текст кнопки и данные обратного вызова для удаления кошелька
    (LEXICON["delete_wallet"], "callback_button_delete_wallet"),
]

# Создание основной клавиатуры с кнопками на основе созданных данных
main_keyboard = create_keyboard(button_data)
