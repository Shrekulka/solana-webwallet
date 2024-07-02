# solana_wallet_telegram_bot/keyboards/back_keyboard.py

from lexicon.lexicon_en import LEXICON
from utils.keyboard_utils import create_inline_keyboard

# Клавиатура "Назад" с одной кнопкой "Назад"
########################################################################################################################
back_button = [
    (LEXICON["button_back"], "callback_button_back"),
]
back_keyboard = create_inline_keyboard(back_button)
########################################################################################################################
