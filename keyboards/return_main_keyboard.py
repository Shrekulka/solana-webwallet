# solana_wallet_telegram_bot/keyboards/return_main_keyboard.py

from lexicon.lexicon_en import LEXICON
from utils.keyboard_utils import create_inline_keyboard

# Клавиатура возврата в главное меню с одной кнопкой "Main menu"
########################################################################################################################
return_main_button = [
    (LEXICON["return_main_keyboard"], "callback_button_return_main_keyboard"),
]
return_main_keyboard = create_inline_keyboard(return_main_button)
########################################################################################################################
