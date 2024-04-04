# solana_wallet_telegram_bot/keyboards/transfer_transaction_keyboards.py

from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from external_services.solana.solana import get_sol_balance, http_client
from lexicon.lexicon_en import LEXICON
from models.models import SolanaWallet

# Словарь для кэширования балансов кошельков
wallet_balances_cache = {}


async def get_wallet_keyboard(user_wallets: List[SolanaWallet]) -> InlineKeyboardMarkup:
    """
    Asynchronously generates a keyboard with buttons for each wallet.

    Args:
        user_wallets (List[SolanaWallet]): List of user's wallets.

    Returns:
        InlineKeyboardMarkup: Keyboard with buttons for each wallet.
    """
    global wallet_balances_cache  # Для доступа к глобальному кэшу

    # Проверяем кэш на наличие балансов кошельков
    if not wallet_balances_cache:
        # Если кэш пуст, запрашиваем балансы для всех кошельков одним запросом
        wallet_addresses = [wallet.wallet_address for wallet in user_wallets]
        balances = await get_sol_balance(wallet_addresses, http_client)

        # Заполняем кэш результатами запроса
        wallet_balances_cache = dict(zip(wallet_addresses, balances))

    # Создаем список кнопок для каждого кошелька
    wallet_buttons = []  # Пустой список кнопок
    count = 1  # Инициализация счетчика

    # Итерация по кошелькам пользователя
    for wallet in user_wallets:
        # Получаем баланс из кэша
        balance = wallet_balances_cache.get(wallet.wallet_address)

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

        # Создаем инлайн-кнопку для кошелька с помощью InlineKeyboardButton
        wallet_button = InlineKeyboardButton(
            # Устанавливаем текст кнопки как сформированную информацию о кошельке
            text=wallet_button_text,
            # Устанавливаем callback_data, включающий в себя префикс "wallet_address" и адрес кошелька
            callback_data=f"wallet_address:{wallet.wallet_address}"
        )

        # Добавляем кнопку в список кнопок
        wallet_buttons.append([wallet_button])
        # Увеличиваем счетчик
        count += 1

    # Добавляем кнопку "Вернуться в главное меню"
    return_to_main_menu_button = InlineKeyboardButton(
        text=LEXICON["button_back"],
        callback_data="callback_button_back"
    )
    wallet_buttons.append([return_to_main_menu_button])

    # Создаем клавиатуру из кнопок
    wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=wallet_buttons)
    return wallet_keyboard  # Возвращаем созданную клавиатуру
