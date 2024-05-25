import traceback

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from web3 import AsyncWeb3
# from sqlalchemy import select

# from database.database import get_db
from config_data.config import CURRENT_BLOCKCHAIN
from external_services.solana.solana import (
    is_valid_wallet_address,
)
from external_services.binance_smart_chain.bsc import (
    is_valid_bsc_wallet_address,
)
from keyboards.back_keyboard import back_keyboard
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from states.states import FSMWallet
from utils.validators import is_valid_wallet_name, is_valid_wallet_description

########### django #########
from django.contrib.auth import get_user_model
from applications.wallet.models import Wallet, Blockchain
from asgiref.sync import sync_to_async


@sync_to_async
def get_user(telegram_id):
    User = get_user_model()
    user = User.objects.filter(telegram_id=telegram_id).first()
    return user

@sync_to_async
def create_wallet(user, wallet_address, name, description, blockchain):
    print("**** blockchain:", blockchain)
    if blockchain == 'bsc':
        w3 = AsyncWeb3()
        # Checksum адрес отличается от не checksum тем, что некоторые буквы в адресе будут в верхнем регистре.
        # Checksum address нужен для того, чтобы убедиться, что адрес валиден и не содержит опечаток.
        wallet_address = w3.to_checksum_address(wallet_address)
        blockchain_choices = Blockchain.BINANCE_SMART_CHAIN

    elif blockchain == 'solana':
        blockchain_choices = Blockchain.SOLANA

    wallet = Wallet.objects.create(
        wallet_address=wallet_address,
        name=name,
        description=description,
        blockchain=blockchain_choices,
    )
    wallet.user.set([user])
    return wallet

############################

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
        blockchain = CURRENT_BLOCKCHAIN

        if blockchain == 'solana':
            # Проверяем валидность адреса кошелька
            if is_valid_wallet_address(wallet_address):
                # Обновляем данные состояния с адресом кошелька
                user = await get_user(telegram_id=message.from_user.id)
                user_wallets = []

                async for w in Wallet.objects.filter(user=user):
                    user_wallets.append(w.wallet_address)

                if wallet_address in user_wallets:
                    await message.answer(LEXICON["this_wallet_already_exists"].format(wallet_address=wallet_address))
                    await message.answer(LEXICON["connect_wallet_address"], reply_markup=back_keyboard)
                else:
                    await state.update_data(wallet_address=wallet_address, blockchain=blockchain)
                    # Отправляем запрос на ввод имени
                    await message.answer(LEXICON["connect_wallet_add_name"], reply_markup=back_keyboard)
                    await state.set_state(FSMWallet.connect_wallet_add_name)

            else:
                # Если адрес невалиден, отправляем сообщение об ошибке и просим ввести адрес заново
                await message.answer(LEXICON["invalid_wallet_address"])
                await message.answer(LEXICON["connect_wallet_address"], reply_markup=back_keyboard)

        if blockchain == 'bsc':
            # Проверяем валидность адреса кошелька
            if is_valid_bsc_wallet_address(wallet_address):
                # Обновляем данные состояния с адресом кошелька
                user = await get_user(telegram_id=message.from_user.id)
                user_wallets = []

                async for w in Wallet.objects.filter(user=user):
                    user_wallets.append(w.wallet_address)

                if wallet_address in user_wallets:
                    await message.answer(LEXICON["this_wallet_already_exists"].format(wallet_address=wallet_address))
                    await message.answer(LEXICON["connect_wallet_address"], reply_markup=back_keyboard)
                else:
                    await state.update_data(wallet_address=wallet_address, blockchain=blockchain)
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
        # Извлекаем блокчейн из данных
        blockchain = data.get("blockchain")

        user = await get_user(telegram_id=message.from_user.id)

        wallet = await create_wallet(
            user=user,
            wallet_address=wallet_address,
            name=name,
            description=description,
            blockchain=blockchain,
        )

        if wallet:
            # Отправляем сообщение об успешном подключении
            await message.answer(LEXICON["wallet_connected_successfully"].format(wallet_address=wallet.wallet_address))

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
