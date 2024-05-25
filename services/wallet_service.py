# solana_wallet_telegram_bot/services/wallet_service.py

import traceback
from decimal import Decimal
from typing import Tuple, Optional, List, Dict

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
# from sqlalchemy import select

from config_data.config import LAMPORT_TO_SOL_RATIO, CURRENT_BLOCKCHAIN
# from database.database import get_db
from external_services.solana.solana import get_sol_balance, http_client
from external_services.binance_smart_chain.bsc import get_bnb_balance, bsc_client
from keyboards.main_keyboard import main_keyboard
from keyboards.transfer_transaction_keyboards import get_wallet_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from states.states import FSMWallet

########### django #########
from django.contrib.auth import get_user_model
from applications.wallet.models import Wallet, Blockchain
from asgiref.sync import sync_to_async

User = get_user_model()

@sync_to_async
def get_user(telegram_id):
    # DjangoUser = get_user_model()
    user = User.objects.filter(telegram_id=telegram_id).first()
    return user

############################


async def retrieve_user_wallets(callback: CallbackQuery) -> Tuple[Optional[User], List[Wallet]]:
    """
        Retrieves user and user wallets from the database.

        Args:
            callback (CallbackQuery): CallbackQuery object containing information about the call.

        Returns:
            Tuple[Optional[User], List[Wallet]]: User object and list of user's Wallet objects.
    """
    user = None  # Инициализация переменной для пользователя
    user_wallets = []  # Инициализация переменной для списка кошельков пользователя

    user = await get_user(telegram_id=callback.from_user.id)

    blockchain = CURRENT_BLOCKCHAIN
    if blockchain == 'bsc':
        blockchain_choices = Blockchain.BINANCE_SMART_CHAIN
    elif blockchain == 'solana':
        blockchain_choices = Blockchain.SOLANA

    if user:

        async for w in Wallet.objects.filter(user=user, blockchain=blockchain_choices):
            user_wallets.append(w)

    # Возвращаем пользователя и его кошельки
    return user, user_wallets


async def handle_no_user_or_wallets(callback: CallbackQuery) -> None:
    """
        Handles the case when no user or wallets are found.

        Args:
            callback (CallbackQuery): CallbackQuery object containing information about the call.

        Returns:
            None
    """
    # Отправляем сообщение об отсутствии зарегистрированных кошельков
    await callback.message.answer(LEXICON["no_registered_wallet"])

    # Отправляем сообщение с предложением вернуться в главное меню с клавиатурой основного меню
    await callback.message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)

    # Отвечаем на запрос пользователя, чтобы избежать ощущения зависания
    await callback.answer()


async def process_wallets_command(callback: CallbackQuery, state: FSMContext, action: str) -> None:
    """
        Handles the command related to wallets.

        Args:
            callback (CallbackQuery): CallbackQuery object containing information about the call.
            state (FSMContext): FSMContext object for working with chat states.
            action (str): Action to perform (balance, transfer, transactions).

        Returns:
            None
    """
    try:
        # Получаем пользователя и список его кошельков из базы данных
        user, user_wallets = await retrieve_user_wallets(callback)

        # Выводим сообщение со списком кошельков
        await callback.message.edit_text(LEXICON['list_sender_wallets'])

        # Проверяем, есть ли пользователь и у него есть ли кошельки
        if user and user_wallets:
            if action == "balance":
                # Если пользователь запрашивает баланс, отправляем информацию о каждом кошельке
                for i, wallet in enumerate(user_wallets):
                    # Получаем баланс кошелька
                    blockchain = CURRENT_BLOCKCHAIN
                    if blockchain == 'solana':
                        balance = await get_sol_balance(wallet.wallet_address, http_client)
                    elif blockchain == 'bsc':
                        balance = await get_bnb_balance(wallet.wallet_address, bsc_client)
                    # Форматируем текст сообщения с информацией о кошельке
                    message_text = LEXICON['wallet_info_template'].format(
                        number=i + 1,
                        name=wallet.name,
                        address=wallet.wallet_address,
                        balance=balance
                    )
                    # Отправляем сообщение с информацией о кошельке
                    await callback.message.answer(message_text)
                # Отправляем сообщение с кнопкой "вернуться в главное меню"
                await callback.message.answer(text=LEXICON["back_to_main_menu"], reply_markup=callback.message.reply_markup)
            else:
                # Если это не запрос баланса, то редактируем сообщение со списком кошельков
                # и отображаем клавиатуру с выбором кошелька
                wallet_keyboard = await get_wallet_keyboard(user_wallets)
                # Редактируем текст сообщения, выводя список кошельков отправителя
                await callback.message.edit_text(LEXICON["list_sender_wallets"], reply_markup=wallet_keyboard)
                # Если пользователь хочет выполнить операцию перевода средств
                if action == "transfer":
                    # Устанавливаем состояние FSM для выбора отправителя
                    await state.set_state(FSMWallet.transfer_choose_sender_wallet)
                # Если пользователь хочет просмотреть список транзакций для выбранного кошелька
                elif action == "transactions":
                    # Устанавливаем состояние FSM для выбора кошелька для просмотра транзакций
                    await state.set_state(FSMWallet.choose_transaction_wallet)
                elif action == "delete":
                    # Устанавливаем состояние FSM для выбора кошелька для удаления
                    await state.set_state(FSMWallet.delete_wallet)
        else:
            # Если пользователь не найден или у него нет кошельков, обрабатываем эту ситуацию
            await handle_no_user_or_wallets(callback)

        # Отвечаем на callback запрос, чтобы избежать зависания и исключений
        await callback.answer()

    except Exception as error:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_{action}_command: {error}\n{detailed_error_traceback}")


async def format_transaction_message(transaction: Dict) -> str:
    """
       Formats the transaction message.

       Args:
           transaction (dict): Transaction data.

       Returns:
           str: Formatted transaction message.
    """
    # Расчет суммы в SOL из лампортов
    amount_in_sol = (transaction.transaction.meta.pre_balances[0] -
                     transaction.transaction.meta.post_balances[0]) / LAMPORT_TO_SOL_RATIO

    # Форматирование суммы в SOL с двумя десятичными знаками
    formatted_amount = '{:.6f}'.format(Decimal(str(amount_in_sol)))

    # Форматирование сообщения о транзакции с использованием лексикона
    transaction_message = LEXICON["transaction_info"].format(
        # Форматирование идентификатора транзакции
        transaction_id='{}...{}'.format(
            str(transaction.transaction.transaction.signatures[0])[:4],  # Берем первые 4 символа
            str(transaction.transaction.transaction.signatures[0])[-4:]  # Берем последние 4 символа
        ),
        # Форматирование счета отправителя
        sender='{}...{}'.format(
            str(transaction.transaction.transaction.message.account_keys[0])[:4],  # Берем первые 4 символа
            str(transaction.transaction.transaction.message.account_keys[0])[-4:]  # Берем последние 4 символа
        ),
        # Форматирование счета получателя
        recipient='{}...{}'.format(
            str(transaction.transaction.transaction.message.account_keys[1])[:4],  # Берем первые 4 символа
            str(transaction.transaction.transaction.message.account_keys[1])[-4:]  # Берем последние 4 символа
        ),
        # Включение суммы в SOL в отформатированное сообщение
        amount_in_sol=formatted_amount
    )
    # Возвращаем отформатированное сообщение о транзакции
    return transaction_message


async def format_transaction_from_db_message(transaction: Dict) -> str:
    """
       Formats the transaction message.

       Args:
           transaction (dict): Transaction data.

       Returns:
           str: Formatted transaction message.
    """
    # Расчет суммы в SOL из лампортов
    amount_in_sol = (transaction.pre_balances - transaction.post_balances) / LAMPORT_TO_SOL_RATIO
    # Форматирование суммы в SOL с двумя десятичными знаками
    formatted_amount = '{:.6f}'.format(Decimal(str(amount_in_sol)))
    # Форматирование сообщения о транзакции с использованием лексикона
    tr_message = LEXICON["transaction_info"].format(
        # Форматирование идентификатора транзакции
        transaction_id='{}...{}'.format(transaction.transaction_id[:4], transaction.transaction_id[-4:]),
        # Форматирование счета отправителя
        sender='{}...{}'.format(transaction.sender[:4], transaction.sender[-4:]),
        # Форматирование счета получателя
        recipient='{}...{}'.format(transaction.recipient[:4], transaction.recipient[-4:]),
        # Включение суммы в SOL в отформатированное сообщение
        amount_in_sol=formatted_amount
    )
    # Возвращаем отформатированное сообщение о транзакции
    return tr_message
