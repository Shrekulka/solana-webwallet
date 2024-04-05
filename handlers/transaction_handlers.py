# solana_wallet_telegram_bot/handlers/transaction_handlers.py
import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from external_services.solana.solana import get_transaction_history
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from states.states import FSMWallet

# Инициализируем роутер уровня модуля
transaction_router: Router = Router()


@transaction_router.callback_query(F.data.startswith("wallet_address:"),
                                   StateFilter(FSMWallet.choose_transaction_wallet))
async def process_choose_transaction_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the button press to select a wallet address for fetching transaction history.

        Arguments:
        callback (CallbackQuery): The callback query object.
        state (FSMContext): The state context of the finite state machine.

        Returns:
        None
    """
    try:
        # Извлекаем адрес кошелька из callback_data
        wallet_address = callback.data.split(":")[1]
        logger.debug(f"Wallet address: {wallet_address}")

        transaction_history = await get_transaction_history(wallet_address)
        logger.debug(f"Transaction history: {transaction_history}")

        if transaction_history:
            # Формируем сообщения для каждой транзакции
            for transaction in transaction_history[:5]:
                transaction_message = LEXICON["transaction_info"].format(
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

                # Отправляем каждую транзакцию в отдельном сообщении
                await callback.message.answer(transaction_message)
        else:
            await callback.answer(LEXICON["empty_history"], show_alert=True, reply_markup=None)

        # Избегаем ощущения, что бот завис, избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in choose_transaction_wallet: {e}\n{detailed_error_traceback}")
        # Отправляем сообщение пользователю о недоступности сервера и просьбе повторить запрос позже
        await callback.answer(LEXICON["server_unavailable"], show_alert=True, reply_markup=None)
        # Возвращаем пользователя в главное меню
        await callback.message.edit_text(LEXICON["back_to_main_menu"])
        await callback.message.edit_reply_markup(reply_markup=main_keyboard)
