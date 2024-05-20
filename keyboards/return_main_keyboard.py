# solana_wallet_telegram_bot/keyboards/return_main_keyboard.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.lexicon_en import LEXICON

# Создание клавиатуры "Назад" с одной кнопкой "Назад", используя InlineKeyboardMarkup
return_main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        # Создание ряда с одной кнопкой "Назад" и соответствующим callback_data
        [InlineKeyboardButton(text=LEXICON["return_main_keyboard"],
                              callback_data="callback_button_return_main_keyboard")]
    ]
)
