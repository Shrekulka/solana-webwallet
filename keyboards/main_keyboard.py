# solana_wallet_telegram_bot/keyboards/main_keyboard.py

from lexicon.lexicon_en import LEXICON
from utils.keyboard_utils import create_inline_keyboard

# Главная клавиатура
########################################################################################################################
main_button = [
    (LEXICON["create_wallet"], "callback_button_create_wallet"),
    (LEXICON["delete_wallet"], "callback_button_delete_wallet"),
    (LEXICON["connect_wallet"], "callback_button_connect_wallet"),
    (LEXICON["balance"], "callback_button_balance"),
    (LEXICON["token_transfer"], "callback_button_transfer"),
    (LEXICON["transaction"], "callback_button_transaction"),
    (LEXICON["crypto_price"], "callback_button_crypto_price")
]
main_keyboard = create_inline_keyboard(main_button)
########################################################################################################################

