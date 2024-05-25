# solana_wallet_telegram_bot/keyboards/transfer_transaction_keyboards.py

import time
from typing import List, Dict

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config_data.config import TRANSACTION_HISTORY_CACHE_DURATION, CURRENT_BLOCKCHAIN
from external_services.solana.solana import get_sol_balance, http_client
from external_services.binance_smart_chain.bsc import get_bnb_balance, bsc_client
from lexicon.lexicon_en import LEXICON
from applications.wallet.models import Wallet

# Создание пустого словаря для кэширования балансов кошельков
wallet_balances_cache: Dict[str, float] = {}
# Инициализация времени последнего обновления кэша
cache_last_updated: float = 0.0


async def get_wallet_keyboard(user_wallets: List[Wallet]) -> InlineKeyboardMarkup:
    """
        Function for creating a keyboard with user wallets.

        Args:
            user_wallets (List[Wallet]): The list of user wallets.

        Returns:
            InlineKeyboardMarkup: The keyboard with wallet buttons.
    """
    global wallet_balances_cache, cache_last_updated

    # Получаем текущее время
    current_time = time.time()

    # Проверяем, нужно ли обновить кэш:
    # Если прошло больше времени, чем TRANSACTION_HISTORY_CACHE_DURATION с момента последнего обновления кэша,
    # или кэш пустой, то обновляем его
    if (current_time - cache_last_updated > TRANSACTION_HISTORY_CACHE_DURATION) or not wallet_balances_cache:
        # Формируем список адресов кошельков пользователя
        wallet_addresses = [wallet.wallet_address for wallet in user_wallets]
        # Получаем балансы кошельков асинхронно
        blockchain = CURRENT_BLOCKCHAIN
        if blockchain == 'solana':
            balances = await get_sol_balance(wallet_addresses, http_client)
        if blockchain == 'bsc':
            balances = await get_bnb_balance(wallet_addresses, bsc_client)
        # Создаем словарь с парами "адрес кошелька - баланс" и обновляем кэш балансов
        wallet_balances_cache = dict(zip(wallet_addresses, balances))
        # Обновляем время последнего обновления кэша
        cache_last_updated = current_time

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

        # Создаем кнопку для кошелька с текстом, содержащим информацию о кошельке, и callback_data,
        # содержащим адрес кошелька
        wallet_button = InlineKeyboardButton(text=wallet_button_text, callback_data=f"wallet_address:{wallet.wallet_address}")

        # Добавляем кнопку в список кнопок
        wallet_buttons.append([wallet_button])
        # Увеличиваем счетчик
        count += 1

    # Создаем кнопку для возврата в главное меню
    return_to_main_menu_button = InlineKeyboardButton(
        text=LEXICON["button_back"],          # Текст кнопки задается из словаря LEXICON
        callback_data="callback_button_back"  # Указываем данные обратного вызова для кнопки
    )

    # Добавляем кнопку в список кнопок, каждая кнопка должна находиться в отдельном списке для формирования столбцов в
    # клавиатуре
    wallet_buttons.append([return_to_main_menu_button])

    # Создаем клавиатуру с кнопками, используя список кнопок
    wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=wallet_buttons)

    # Возвращаем сформированную клавиатуру
    return wallet_keyboard
