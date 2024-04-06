# solana_wallet_telegram_bot/keyboards/back_keyboard.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.lexicon_en import LEXICON

# Создание клавиатуры "Назад" с одной кнопкой "Назад", используя InlineKeyboardMarkup
back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        # Создание ряда с одной кнопкой "Назад" и соответствующим callback_data
        [InlineKeyboardButton(text=LEXICON["button_back"], callback_data="callback_button_back")]
    ]
)
