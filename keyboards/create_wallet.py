# solana_wallet_telegram_bot/keyboards/create_wallet.py


from lexicon.lexicon_en import LEXICON
from utils.keyboard_utils import create_inline_keyboard

# Клавиатура для создания кошелька
########################################################################################################################
create_wallet_button = [
    (LEXICON["create_wallet_constructor"], "callback_button_create_wallet_constructor"),
    (LEXICON["create_wallet_from_seed"], "callback_button_create_wallet_from_seed"),
    (LEXICON["return_main_keyboard"], "callback_button_return_main_keyboard"),
]
create_wallet_keyboard = create_inline_keyboard(create_wallet_button)
########################################################################################################################
