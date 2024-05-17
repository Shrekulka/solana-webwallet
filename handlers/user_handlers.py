# solana-webwallet/handlers/user_handlers.py

import traceback

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
# from sqlalchemy import select

# from database.database import get_db
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from services.wallet_service import process_wallets_command
from states.states import FSMWallet
from config_data.config import SOLANA_NODE_URL

########### django #########
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async


@sync_to_async
def update_or_create_user(telegram_id, defaults):
    User = get_user_model()
    user, created = User.objects.update_or_create(telegram_id=telegram_id, defaults=defaults)
    return user, created

############################

# Инициализируем роутер уровня модуля
user_router: Router = Router()


@user_router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext) -> None:
    """
        Handler for the start bot command.

        Args:
            message (Message): The incoming message.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        # Отправка сообщения пользователю с приветственным текстом и клавиатурой
        await message.answer(
            LEXICON["/start"].format(
                first_name=message.from_user.first_name,
                node=SOLANA_NODE_URL,
            ),
            reply_markup=main_keyboard,
        )

        user_data = {
            'username': '{}'.format(message.from_user.id),
            'telegram_language': message.from_user.language_code or 'en',
            'telegram_username': message.from_user.username[:64] if message.from_user.username else '',
            'first_name': message.from_user.first_name[:60] if message.from_user.first_name else '',
            'last_name': message.from_user.last_name[:60] if message.from_user.last_name else '',
            'is_bot': 'Yes' if message.from_user.is_bot else 'No',
            'raw_data': message.from_user.dict(),
        }

        user, created = await update_or_create_user(telegram_id=message.from_user.id, defaults=user_data)
    except Exception as e:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_start_command: {e}\n{detailed_send_message_error}")


# Объявление функции обработки команды "/help"
@user_router.message(Command(commands='help'), StateFilter(default_state))
async def process_help_command(message: Message, state: FSMContext) -> None:
    """
        Handler for the "/help" command.

        Args:
            message (Message): The incoming message.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        # Отправляем сообщение со справочной информацией о командах из лексикона
        await message.answer(LEXICON["/help"])

        await message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)
    except Exception as e:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_create_wallet_command: {e}\n{detailed_send_message_error}")


@user_router.message(~CommandStart(), ~Command(commands='help'), StateFilter(default_state))
async def process_unexpected_input(message: Message) -> None:
    """
        Handler for unexpected messages in the default_state.

        Args:
            message (Message): Incoming message.

        Returns:
            None
    """
    try:
        # Проверяем, может ли бот редактировать сообщения
        if message.chat.type == 'private':  # Проверяем, что чат является приватным
            if message.text:  # Проверяем, есть ли текст в сообщении
                await message.answer(LEXICON["unexpected_input"])
            else:
                logger.warning("Received message without text. Cannot edit.")
        else:
            logger.warning("Received message in a non-private chat. Cannot edit.")
    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_unexpected_input: {error}\n{detailed_send_message_error}")


@user_router.callback_query(F.data == "callback_button_create_wallet", StateFilter(default_state))
async def process_create_wallet_command(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handler for selecting the "Create Wallet" option from the menu.

        Args:
            callback (CallbackQuery): The callback object.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        # Отправляем сообщение с просьбой ввести имя для кошелька
        await callback.message.edit_text(LEXICON["create_name_wallet"])
        # Переход в состояние добавления имени кошелька
        await state.set_state(FSMWallet.create_wallet_add_name)
        # Избегаем ощущения, что бот завис и избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_create_wallet_command: {error}\n{detailed_send_message_error}")


@user_router.callback_query(F.data == "callback_button_create_wallet_from_seed", StateFilter(default_state))
async def process_create_wallet_from_seed_command(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handler for selecting the "Create Wallet From Seed" option from the menu.

        Args:
            callback (CallbackQuery): The callback object.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        await callback.message.edit_text(LEXICON["create_seed_wallet"])
        await state.set_state(FSMWallet.create_wallet_from_seed_add_seed)
        # Избегаем ощущения, что бот завис и избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_create_wallet_from_seed_command: {error}\n{detailed_send_message_error}")


@user_router.callback_query(F.data == "callback_button_connect_wallet", StateFilter(default_state))
async def process_connect_wallet_command(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handler for selecting the "Connect Wallet" option from the menu.

        Args:
            callback (CallbackQuery): The callback object.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        # Запрашиваем у пользователя адрес кошелька
        await callback.message.edit_text(LEXICON["connect_wallet_address"])
        # Переход в состояние добавления
        await state.set_state(FSMWallet.connect_wallet_add_address)
        # Избегаем ощущения, что бот завис и избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_connect_wallet_command: {error}\n{detailed_send_message_error}")


@user_router.callback_query(F.data == "callback_button_transfer", StateFilter(default_state))
async def process_transfer_token_command(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the command for transferring tokens.

        Args:
            callback (CallbackQuery): CallbackQuery object containing information about the call.
            state (FSMContext): FSMContext object for working with chat states.

        Returns:
            None
    """
    await process_wallets_command(callback, state, "transfer")


@user_router.callback_query(F.data == "callback_button_balance", StateFilter(default_state))
async def process_balance_command(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает команду для получения баланса кошелька.

    Args:
        callback (CallbackQuery): Объект CallbackQuery, содержащий информацию о вызове.
        state (FSMContext): Объект FSMContext для работы с состояниями чата.

    Returns:
        None
    """
    await process_wallets_command(callback, state, "balance")


@user_router.callback_query(F.data == "callback_button_transaction", StateFilter(default_state))
async def process_transactions_command(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the command for viewing transactions.

        Args:
            callback (CallbackQuery): CallbackQuery object containing information about the call.
            state (FSMContext): FSMContext object for working with chat states.

        Returns:
            None
    """
    await process_wallets_command(callback, state, "transactions")
