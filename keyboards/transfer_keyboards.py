# solana_wallet_telegram_bot/keyboards/transfer_keyboards.py
from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from external_services.solana.solana import get_sol_balance, http_client
from lexicon.lexicon_en import LEXICON
from models.models import SolanaWallet


async def get_wallet_keyboard(user_wallets: List[SolanaWallet]) -> InlineKeyboardMarkup:
    """
    Asynchronously generates a keyboard with buttons for each wallet.

    Args:
        user_wallets (List[SolanaWallet]): List of user's wallets.

    Returns:
        InlineKeyboardMarkup: Keyboard with buttons for each wallet.
    """
    # Создаем список кнопок для каждого кошелька
    wallet_buttons = []  # Пустой список кнопок
    count = 1  # Инициализация счетчика

    # Итерация по кошелькам пользователя
    for wallet in user_wallets:
        # Получаем баланс солана для каждого кошелька
        balance = await get_sol_balance(wallet.wallet_address, http_client)

        # Форматируем информацию о кошельке с использованием шаблона из лексикона
        wallet_info = LEXICON["wallet_info_template"].format(
            number=count,
            name=wallet.name,
            address=wallet.wallet_address,
            balance=balance
        )

        # Создаем список строк из информации о кошельке
        wallet_info_lines = wallet_info.split('\n')

        # Создаем текст кнопки, объединяя строки информации о кошельке с помощью переноса строки
        wallet_button_text = '\n'.join(wallet_info_lines)

        # Создаем инлайн-кнопку для кошелька
        wallet_button = InlineKeyboardButton(
            text=wallet_button_text,
            callback_data=f"wallet_id:{wallet.id}"  # Уникальный идентификатор кошелька для обратного вызова
        )
        # Добавляем кнопку в список кнопок
        wallet_buttons.append([wallet_button])
        # Увеличиваем счетчик
        count += 1

    # Создаем клавиатуру из кнопок
    wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=wallet_buttons)
    return wallet_keyboard  # Возвращаем созданную клавиатуру
