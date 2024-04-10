# solana_wallet_telegram_bot/services/wallet_service.py

import traceback
from decimal import Decimal
from typing import Tuple, Optional, List, Dict

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import select

from config_data.config import LAMPORT_TO_SOL_RATIO
from database.database import get_db
from external_services.solana.solana import get_sol_balance, http_client
from keyboards.main_keyboard import main_keyboard
from keyboards.transfer_transaction_keyboards import get_wallet_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from models.models import User, SolanaWallet
from states.states import FSMWallet


async def retrieve_user_wallets(callback: CallbackQuery) -> Tuple[Optional[User], List[SolanaWallet]]:
    """
        Retrieves user and user wallets from the database.

        Args:
            callback (CallbackQuery): CallbackQuery object containing information about the call.

        Returns:
            Tuple[Optional[User], List[SolanaWallet]]: User object and list of user's SolanaWallet objects.
    """
    user = None  # Инициализация переменной для пользователя
    user_wallets = []  # Инициализация переменной для списка кошельков пользователя

    async with await get_db() as session:
        # Получаем пользователя по его telegram_id
        user = await session.execute(select(User).filter_by(telegram_id=callback.from_user.id))
        # Получаем объект пользователя из результата запроса
        user = user.scalar()

        # Если пользователь найден
        if user:
            # Получаем кошельки пользователя из базы данных, фильтруя по идентификатору пользователя
            user_wallets = await session.execute(select(SolanaWallet).filter_by(user_id=user.id))
            # Преобразуем результат запроса в список скалярных значений
            user_wallets = user_wallets.scalars().all()
            # Преобразуем список скалярных значений в список кошельков
            user_wallets = list(user_wallets)

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
                    balance = await get_sol_balance(wallet.wallet_address, http_client)
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
                await callback.message.answer(text=LEXICON["back_to_main_menu"],
                                              reply_markup=callback.message.reply_markup)
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
