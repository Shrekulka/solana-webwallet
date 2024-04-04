# solana_wallet_telegram_bot/keyboards/back_keyboard.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.lexicon_en import LEXICON

back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON["button_back"], callback_data="callback_button_back")]
    ]
)
