# solana_wallet_telegram_bot/handlers/transaction_handlers.py
import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from external_services.solana.solana import http_client, get_transaction_history
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from states.states import FSMWallet

# Инициализируем роутер уровня модуля
transaction_router: Router = Router()


@transaction_router.callback_query(F.data.startswith("wallet_address:"),
                                   StateFilter(FSMWallet.choose_transaction_wallet))
async def process_choose_transaction_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the user's selection of the wallet for transaction.

        Args:
            callback (CallbackQuery): The callback query object containing data about the selected wallet.
            state (FSMContext): The state context for working with chat states.

        Raises:
            Exception: If an error occurs while processing the request.

        Returns:
            None
    """
    try:
        # Извлекаем адрес кошелька из callback_data
        wallet_address = callback.data.split(":")[1]
        logger.debug(f"Wallet address: {wallet_address}")

        transaction_history = await get_transaction_history(wallet_address, http_client)
        logger.debug(f"Transaction history: {transaction_history}")
        if transaction_history:

            # for i, tr in enumerate(transaction_history):
            #     print(f'*** {i + 1}. transaction: {tr}\n')

            # Если история транзакций существует, формируем сообщение с информацией о транзакциях.
            # for async client
            transaction_messages = [
                # Форматирование каждого сообщения о транзакции с помощью LEXICON и данных из истории транзакций.
                LEXICON["transaction_info"].format(
                    # Идентификатор транзакции, обрезанный до первых 8 символов для краткости.
                    transaction_id='{}...{}'.format(
                        str(transaction.transaction.transaction.signatures[0])[:4],
                        str(transaction.transaction.transaction.signatures[0])[-4:],
                    ),
                    # Отправитель транзакции - первый аккаунт в списке аккаунтов сообщения.
                    sender='{}...{}'.format(
                        str(transaction.transaction.transaction.message.account_keys[0])[:4],
                        str(transaction.transaction.transaction.message.account_keys[0])[-4:],
                    ),
                    # Получатель транзакции - второй аккаунт в списке аккаунтов сообщения.
                    recipient='{}...{}'.format(
                        str(transaction.transaction.transaction.message.account_keys[1])[:4],
                        str(transaction.transaction.transaction.message.account_keys[1])[-4:],
                    ),
                    # Разница в балансе отправителя до и после транзакции, выраженная в SOL.
                    amount=transaction.transaction.meta.pre_balances[0] - transaction.transaction.meta.post_balances[0]
                )
                # Итерация по каждой транзакции в истории транзакций.
                for transaction in transaction_history
            ]

            for i, tr_mes in enumerate(transaction_messages):
                print(f'{i}. transaction_messages: {tr_mes}\n\n')

            # TODO ERROR: aiogram.exceptions.TelegramBadRequest: Telegram server says - Bad Request: MESSAGE_TOO_LONG
            await callback.answer(f'Last transaction: \n{transaction_messages[0]}')
        else:
            await callback.answer(LEXICON["empty_history"], show_alert=True, reply_markup=None)

        # Избегаем ощущения, что бот завис, избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in choose_transaction_wallet: {e}\n{detailed_error_traceback}")
