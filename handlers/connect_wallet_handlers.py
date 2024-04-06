# solana_wallet_telegram_bot/handlers/connect_wallet_handlers.py
import traceback

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from database.database import get_db
from external_services.solana.solana import (
    is_valid_wallet_address,
)
from keyboards.back_keyboard import back_keyboard
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from models.models import SolanaWallet, User
from states.states import FSMWallet
from utils.validators import is_valid_wallet_name, is_valid_wallet_description

# Инициализируем роутер уровня модуля
connect_wallet_router: Router = Router()


@connect_wallet_router.message(StateFilter(FSMWallet.connect_wallet_add_address))
async def process_connect_wallet_address(message: Message, state: FSMContext) -> None:
    """
        Handler for entering the wallet address for connection.

        Args:
            message (Message): The incoming message.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        # Извлекаем адрес кошелька из текста сообщения
        wallet_address = message.text
        # Проверяем валидность адреса кошелька
        if is_valid_wallet_address(wallet_address):
            # Обновляем данные состояния с адресом кошелька
            async with await get_db() as session:
                user = await session.execute(select(User).filter_by(telegram_id=message.from_user.id))
                user = user.scalar()

                user_wallets = await session.execute(select(SolanaWallet).filter_by(user_id=user.id))
                user_wallets = user_wallets.scalars().all()

                if user_wallets and (wallet_address in [w.wallet_address for w in user_wallets]):
                    await message.answer(
                        LEXICON["this_wallet_already_exists"].format(wallet_address=wallet_address))
                    await message.answer(LEXICON["connect_wallet_address"], reply_markup=back_keyboard)
                else:
                    await state.update_data(wallet_address=wallet_address)
                    # Отправляем запрос на ввод имени
                    await message.answer(LEXICON["connect_wallet_add_name"], reply_markup=back_keyboard)
                    await state.set_state(FSMWallet.connect_wallet_add_name)

        else:
            # Если адрес невалиден, отправляем сообщение об ошибке и просим ввести адрес заново
            await message.answer(LEXICON["invalid_wallet_address"])
            await message.answer(LEXICON["connect_wallet_address"], reply_markup=back_keyboard)
    except Exception as e:
        # Обработка ошибок и запись подробной информации в лог
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_connect_wallet_address: {e}\n{detailed_error_traceback}")


@connect_wallet_router.message(StateFilter(FSMWallet.connect_wallet_add_name),
                               lambda message: is_valid_wallet_name(message.text))
async def process_connect_wallet_name(message: Message, state: FSMContext) -> None:
    """
        Handler for entering the wallet name.

        Args:
            message (Message): The incoming message.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        # Сохраняем введенное имя кошелька в состояние
        await state.update_data(wallet_name=message.text)

        # Получаем данные из состояния
        data = await state.get_data()

        # Извлекаем имя кошелька из данных
        name = data.get("wallet_name")

        # Отправляем подтверждение с введенным именем кошелька
        await message.answer(text=LEXICON["wallet_name_confirmation"].format(wallet_name=name))

        # Запрашиваем ввод описания кошелька
        await message.answer(text=LEXICON["connect_wallet_add_description"], reply_markup=back_keyboard)

        # Переходим к добавлению описания кошелька
        await state.set_state(FSMWallet.connect_wallet_add_description)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_connect_wallet_name: {e}\n{detailed_error_traceback}")


@connect_wallet_router.message(StateFilter(FSMWallet.connect_wallet_add_name))
async def process_invalid_connect_wallet_name(message: Message, state: FSMContext) -> None:
    """
        Handler for incorrect wallet name input.

        Args:
            message (Message): The incoming message.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        # Отправляем сообщение о некорректном имени кошелька
        await message.answer(text=LEXICON["invalid_wallet_name"])

        # Запрашиваем ввод имени кошелька заново
        await message.answer(text=LEXICON["wallet_name_prompt"])
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_invalid_wallet_name: {e}\n{detailed_error_traceback}")


@connect_wallet_router.message(StateFilter(FSMWallet.connect_wallet_add_description),
                               lambda message: is_valid_wallet_description(message.text))
async def process_connect_wallet_description(message: Message, state: FSMContext) -> None:
    """
        Handles the user input of the wallet description during connection.

        Args:
            message (Message): The user message containing the wallet description.
            state (FSMContext): The state context for managing chat states.

        Returns:
            None
    """
    try:
        # Обновляем данные состояния, добавляя введенное описание
        await state.update_data(description=message.text)
        # Получаем данные из состояния
        data = await state.get_data()
        # Извлекаем имя кошелька из данных
        name = data.get("wallet_name")
        # Извлекаем описание кошелька из данных
        description = data.get("description")
        # Извлекаем адрес кошелька из данных (если он есть)
        wallet_address = data.get("wallet_address")

        # Создаем соединение с базой данных
        async with await get_db() as session:
            user = await session.execute(select(User).filter_by(telegram_id=message.from_user.id))
            user = user.scalar()

            wallet = await SolanaWallet.connect_wallet(
                session, user.id, wallet_address, name, description,
            )
            # Отправляем сообщение об успешном подключении кошелька и очищаем состояние
            await message.answer(
                LEXICON["wallet_connected_successfully"].format(wallet_address=wallet.wallet_address))

            # Очищаем состояние после добавления кошелька
            await state.clear()
            # Отправляем сообщение с предложением продолжить и клавиатурой основного меню
            await message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_connect_wallet_description: {e}\n{detailed_error_traceback}")


@connect_wallet_router.message(StateFilter(FSMWallet.connect_wallet_add_description))
async def process_invalid_wallet_description(message: Message, state: FSMContext) -> None:
    """
        Handler for invalid wallet description input.

        Args:
            message (Message): The incoming message.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        # Отправляем сообщение о недопустимом описании кошелька
        await message.answer(text=LEXICON["invalid_wallet_description"])
        # Запрашиваем ввод описания кошелька еще раз
        await message.answer(text=LEXICON["wallet_description_prompt"])
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_invalid_wallet_description: {e}\n{detailed_error_traceback}")
