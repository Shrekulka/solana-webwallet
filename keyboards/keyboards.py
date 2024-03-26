# solana_wallet_telegram_bot/keyboards/main_keyboard.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.lexicon_en import LEXICON

# Создание объектов кнопок с текстом из словаря и соответствующими callback_data
button_create_wallet = InlineKeyboardButton(text=LEXICON["create_wallet"],
                                            callback_data="callback_button_create_wallet")

button_connect_wallet = InlineKeyboardButton(text=LEXICON["connect_wallet"],
                                             callback_data="callback_button_connect_wallet")

button_balance = InlineKeyboardButton(text=LEXICON["balance"], callback_data="callback_button_balance")

button_price = InlineKeyboardButton(text=LEXICON["token_price"], callback_data="callback_button_price")

button_buy = InlineKeyboardButton(text=LEXICON["token_buy"], callback_data="callback_button_buy")

button_sell = InlineKeyboardButton(text=LEXICON["token_sell"], callback_data="callback_button_sell")

button_transfer = InlineKeyboardButton(text=LEXICON["token_transfer"], callback_data="callback_button_transfer")

button_transactions = InlineKeyboardButton(text=LEXICON["transaction"], callback_data="callback_button_transaction")

button_delete_wallet = InlineKeyboardButton(text=LEXICON["delete_wallet"],
                                            callback_data="callback_button_delete_wallet")

button_settings = InlineKeyboardButton(text=LEXICON["settings"], callback_data="callback_button_settings")

button_donate = InlineKeyboardButton(text=LEXICON["donate"], callback_data="callback_button_donate")

# Формирование списка списков кнопок, чтобы каждая кнопка была в отдельном списке
wallet_buttons = [[button_create_wallet], [button_connect_wallet], [button_balance], [button_price], [button_buy],
                  [button_sell], [button_transfer], [button_transactions], [button_delete_wallet], [button_settings],
                  [button_donate]]

# Создание клавиатуры инлайн-кнопок с указанием списка кнопок
wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=wallet_buttons)
