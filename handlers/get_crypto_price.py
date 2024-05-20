# solana_wallet_telegram_bot/handlers/get_crypto_price.py

import traceback

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from external_services.crypto_price.crypto_price import get_crypto_prices
from keyboards.return_main_keyboard import return_main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from states.states import FSMWallet

# Инициализируем роутер уровня модуля
crypto_price_router: Router = Router()


@crypto_price_router.message(StateFilter(FSMWallet.crypto_price_input))
async def process_crypto_input(message: Message, state: FSMContext) -> None:
    """
        Processes input of cryptocurrency symbol and currency.

        Args:
        message (Message): Incoming message.
        state (FSMContext): FSMContext object for chat state management.

        Returns:
            None
    """
    try:
        # Преобразуем текст сообщения пользователя в верхний регистр, чтобы обработать символ криптовалюты
        crypto_symbol = message.text.upper()
        # Получаем цены для указанного символа криптовалюты
        prices = await get_crypto_prices(crypto_symbol)

        if prices:
            # Формируем заголовок результата с указанием символа криптовалюты и валюты
            result_text = LEXICON["crypto_price_result_header"].format(crypto_symbol=crypto_symbol, currency="USDT")

            # Итерируемся по полученным ценам для различных бирж
            for exchange, price_data in prices.items():
                # Проверяем наличие ключа "last_price" в данных о цене криптовалюты на бирже
                if "last_price" in price_data:
                    # Если цена доступна, добавляем информацию о цене к результату
                    result_text += f"\n{LEXICON['crypto_price_result_exchange'].format(exchange_name=exchange)}"
                    result_text += LEXICON["crypto_price_result_line"].format(crypto_symbol=crypto_symbol,
                                                                              price=price_data["last_price"],
                                                                              currency="USDT")
                else:
                    # Если цена недоступна, добавляем информацию об отсутствии данных к результату
                    result_text += f"\n{LEXICON['crypto_price_result_exchange'].format(exchange_name=exchange)}"
                    result_text += LEXICON["no_data_available"]

            # Отправляем результат пользователю с клавиатурой возврата в главное меню
            await message.answer(result_text, reply_markup=return_main_keyboard)
        else:
            # Если не удалось получить цены, сообщаем пользователю об ошибке
            await message.answer(LEXICON["crypto_price_error"], reply_markup=return_main_keyboard)

        # Очищаем состояние FSM после обработки запроса
        await state.clear()

    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_crypto_input: {error}\n{detailed_send_message_error}")

