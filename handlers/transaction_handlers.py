# solana_wallet_telegram_bot/handlers/transaction_handlers.py
import asyncio
import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery

from external_services.solana.solana import get_transaction_history
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from services.wallet_service import format_transaction_message
from states.states import FSMWallet
from config_data.config import SOLANA_NODE_URL

# Инициализируем роутер уровня модуляz
transaction_router: Router = Router()


@transaction_router.callback_query(F.data.startswith("wallet_address:"),
                                   StateFilter(FSMWallet.choose_transaction_wallet))
async def process_choose_transaction_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the button press to select a wallet address for fetching transaction history.

        Args:
            callback (CallbackQuery): The callback query object.
            state (FSMContext): The state context of the finite state machine.

        Returns:
            None
    """
    try:
        # Извлекаем адрес кошелька из callback_data
        wallet_address = callback.data.split(":")[1]
        transaction_history = []

        if "api.devnet.solana.com" not in SOLANA_NODE_URL:
            # Получаем историю транзакций кошелька по его адресу.
            transaction_history = await get_transaction_history(wallet_address)

        if transaction_history:
            # Создаем список задач на форматирование сообщений о транзакциях
            transaction_tasks = [format_transaction_message(transaction) for transaction in transaction_history]

            # Используем asyncio.gather для параллельной обработки транзакций
            transaction_messages = await asyncio.gather(*transaction_tasks)

            # Объединяем все сообщения в одну строку с разделителем '\n\n'
            combined_message = '\n\n'.join(transaction_messages)

            # Отправляем объединенное сообщение
            await callback.message.answer(combined_message)
        else:
            # Отправляем ответ пользователю с сообщением о пустой истории транзакций
            await callback.answer(LEXICON["empty_history"], show_alert=True, reply_markup=None)

        # Очищаем состояние перед завершением
        await state.clear()

        # Отправляем сообщение с инструкцией о продолжении и клавиатурой основных кнопок
        await callback.message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)

        # Отвечаем на callback запрос, чтобы избежать ощущения зависания и исключений
        # await callback.answer()
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in choose_transaction_wallet: {e}\n{detailed_error_traceback}")
        # Отправляем сообщение пользователю о недоступности сервера и просьбе повторить запрос позже
        await callback.answer(LEXICON["server_unavailable"], show_alert=True, reply_markup=None)
        # Возвращаем пользователя в главное меню
        # await callback.message.delete()
        await callback.message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)
        await state.set_state(default_state)

        await callback.answer()
