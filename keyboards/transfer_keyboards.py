# solana_wallet_telegram_bot/keyboards/transfer_keyboards.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.lexicon_en import LEXICON

# Создание объектов кнопок с текстом из словаря и соответствующими callback_data
button_save_wallet = InlineKeyboardButton(text=LEXICON["save_wallet"], callback_data="callback_button_save_wallet")

button_cancel = InlineKeyboardButton(text=LEXICON["cancel"], callback_data="callback_button_cancel")

# Формирование списка списков кнопок, чтобы каждая кнопка была в отдельном списке
transfer_buttons = [[button_save_wallet], [button_cancel]]

# Создание клавиатуры инлайн-кнопок с указанием списка кнопок
transfer_keyboard = InlineKeyboardMarkup(inline_keyboard=transfer_buttons)
