# solana_wallet_telegram_bot/services/wallet_service.py

import traceback
from typing import Tuple, Optional, List

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import select

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
    user = None
    user_wallets = []

    async with await get_db() as session:
        # Получаем пользователя по его telegram_id
        user = await session.execute(select(User).filter_by(telegram_id=callback.from_user.id))
        user = user.scalar()

        # Если пользователь найден
        if user:
            # Получаем кошельки пользователя
            user_wallets = await session.execute(select(SolanaWallet).filter_by(user_id=user.id))
            user_wallets = user_wallets.scalars().all()
            user_wallets = list(user_wallets)

    return user, user_wallets


async def handle_no_user_or_wallets(callback: CallbackQuery) -> None:
    """
    Handles the case when no user or wallets are found.

    Args:
        callback (CallbackQuery): CallbackQuery object containing information about the call.

    Returns:
        None
    """
    await callback.message.answer(LEXICON["no_registered_wallet"])
    await callback.message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)
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
        user, user_wallets = await retrieve_user_wallets(callback)

        # Выводим сообщение со списком кошельков
        await callback.message.edit_text(LEXICON['list_sender_wallets'])

        # Если пользователь есть и у него есть кошельки
        if user and user_wallets:
            if action == "balance":
                # Отправляем информацию о каждом кошельке
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
                await callback.message.answer(text=LEXICON["back_to_main_menu"],
                                              reply_markup=callback.message.reply_markup)

            else:
                # Получаем клавиатуру с кнопками для выбора кошелька
                wallet_keyboard = await get_wallet_keyboard(user_wallets)
                # Редактируем сообщение с клавиатурой кошельков
                await callback.message.edit_text(LEXICON["list_sender_wallets"], reply_markup=wallet_keyboard)
                if action == "transfer":
                    # Устанавливаем состояние FSM для выбора отправителя
                    await state.set_state(FSMWallet.transfer_choose_sender_wallet)
                elif action == "transactions":
                    # Устанавливаем состояние FSM для выбора отправителя
                    await state.set_state(FSMWallet.choose_transaction_wallet)
        else:
            # Если пользователь не найден или у него нет кошельков
            await handle_no_user_or_wallets(callback)

        # Избегаем ощущения, что бот завис и избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()

    except Exception as error:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_{action}_command: {error}\n{detailed_error_traceback}")
