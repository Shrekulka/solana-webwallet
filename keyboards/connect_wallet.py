# solana_wallet_telegram_bot/keyboards/connect_wallet.py
from aiogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup

from config_data.config import WEB_APP_URL
from lexicon.lexicon_en import LEXICON
from utils.keyboard_utils import create_inline_keyboard

# 1) Клавиатура для подключения кошелька
########################################################################################################################
connect_wallet_button = [
    (LEXICON["connect_wallet_constructor"], "callback_button_connect_wallet_constructor"),
    (LEXICON["connect_wallet_from_seed"], "callback_button_connect_wallet_from_seed"),
    (LEXICON["connect_wallet_qr"], "callback_button_connect_wallet_from_qr"),
    (LEXICON["return_main_keyboard"], "callback_button_return_main_keyboard"),
]
connect_wallet_keyboard = create_inline_keyboard(connect_wallet_button)
########################################################################################################################

# # 2) Клавиатура для подключения кошелька с использованием Web Apps
# ########################################################################################################################

button_connect_wallet_qr = KeyboardButton(text=LEXICON["connect_wallet_qr"], web_app=WebAppInfo(url=WEB_APP_URL))
button_back = KeyboardButton(text=LEXICON["button_back"])

connect_wallet_from_qr_keyboard = ReplyKeyboardMarkup(
    keyboard=[[button_connect_wallet_qr, button_back]],
    one_time_keyboard=True,
    resize_keyboard=True,
    input_field_placeholder=LEXICON["connect_wallet_qr_scan_code"]
)
########################################################################################################################
