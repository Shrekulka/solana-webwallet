# solana_wallet_telegram_bot/handlers/create_wallet_handlers.py

import traceback

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from database.database import get_db
from keyboards.back_keyboard import back_keyboard
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from models.models import SolanaWallet, User
from states.states import FSMWallet
from utils.validators import is_valid_wallet_name, is_valid_wallet_description
from external_services.solana.solana import create_solana_wallet, is_valid_wallet_address

########### django #########
from django.contrib.auth import get_user_model
from applications.wallet.models import Wallet
from asgiref.sync import sync_to_async


@sync_to_async
def get_user(telegram_id):
    DjangoUser = get_user_model()
    user = DjangoUser.objects.filter(telegram_id=telegram_id).first()
    return user

@sync_to_async
def create_wallet(user, wallet_address, name, description):
    wallet = Wallet.objects.create(user=user, wallet_address=wallet_address, name=name, description=description)
    return wallet

############################

# Инициализируем роутер уровня модуля
create_wallet_router: Router = Router()


@create_wallet_router.message(StateFilter(FSMWallet.create_wallet_add_name),
                              lambda message: message.text and is_valid_wallet_name(message.text))
async def process_wallet_name(message: Message, state: FSMContext) -> None:
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
        await message.answer(text=LEXICON["create_description_wallet"], reply_markup=back_keyboard)

        # Переходим к добавлению описания кошелька
        await state.set_state(FSMWallet.create_wallet_add_description)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_wallet_name: {e}\n{detailed_error_traceback}")


@create_wallet_router.message(StateFilter(FSMWallet.create_wallet_add_name))
async def process_invalid_wallet_name(message: Message, state: FSMContext) -> None:
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
        await message.answer(text=LEXICON["create_name_wallet"], reply_markup=back_keyboard)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_invalid_wallet_name: {e}\n{detailed_error_traceback}")


@create_wallet_router.message(StateFilter(FSMWallet.create_wallet_add_description),
                              lambda message: message.text and is_valid_wallet_description(message.text))
async def process_wallet_description(message: Message, state: FSMContext) -> None:
    """
        Handles the user input of the wallet description during creation.

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

        user = await get_user(telegram_id=message.from_user.id)
        wallet_address, private_key, words = await create_solana_wallet()
        wallet = await create_wallet(user=user, wallet_address=wallet_address, name=name, description=description)
        if wallet:
            await state.update_data(sender_address=wallet.wallet_address, sender_private_key=private_key)

        # Если адреса кошелька нет, выводим сообщение об успешном создании и возвращаемся в главное меню
        await message.answer(
            LEXICON["wallet_created_successfully"].format(wallet_name=wallet.name,
                                                          wallet_description=wallet.description,
                                                          wallet_address=wallet.wallet_address,
                                                          private_key=private_key,
                                                          seed_phrase=words))
        # Очищаем состояние после добавления кошелька
        await state.clear()
        # Отправляем сообщение с предложением продолжить и клавиатурой основного меню
        await message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_wallet_description: {e}\n{detailed_error_traceback}")


# @create_wallet_router.message(StateFilter(FSMWallet.create_wallet_add_description),
#                               lambda message: message.text and is_valid_wallet_description(message.text))
# async def process_wallet_description(message: Message, state: FSMContext) -> None:
#     """
#         Handles the user input of the wallet description during creation.

#         Args:
#             message (Message): The user message containing the wallet description.
#             state (FSMContext): The state context for managing chat states.

#         Returns:
#             None
#     """
#     try:
#         # Обновляем данные состояния, добавляя введенное описание
#         await state.update_data(description=message.text)
#         # Получаем данные из состояния
#         data = await state.get_data()
#         # Извлекаем имя кошелька из данных
#         name = data.get("wallet_name")
#         # Извлекаем описание кошелька из данных
#         description = data.get("description")
#         # Извлекаем адрес кошелька из данных (если он есть)
#         wallet_address = data.get("wallet_address")
#         # Создаем соединение с базой данных
#         async with await get_db() as session:
#             user = await session.execute(select(User).filter_by(telegram_id=message.from_user.id))
#             user = user.scalar()

#             # Если wallet_address есть в данных состояния, обновляем существующий кошелек
#             if wallet_address:
#                 wallet = await SolanaWallet.update_wallet(session, user.id, wallet_address, name=name,
#                                                           description=description)
#                 if wallet is None:  # Если кошелек не найден, создаем новый
#                     wallet, private_key = await SolanaWallet.wallet_create(session, user.id, name=name,
#                                                                            description=description)
#                     await state.update_data(sender_address=wallet.wallet_address, sender_private_key=private_key)
#             # Иначе создаем новый кошелек
#             else:
#                 wallet, private_key = await SolanaWallet.wallet_create(session, user.id, name=name,
#                                                                        description=description)
#                 await state.update_data(sender_address=wallet.wallet_address, sender_private_key=private_key)

#         # Если адреса кошелька нет, выводим сообщение об успешном создании и возвращаемся в главное меню
#         await message.answer(
#             LEXICON["wallet_created_successfully"].format(wallet_name=wallet.name,
#                                                           wallet_description=wallet.description,
#                                                           wallet_address=wallet.wallet_address,
#                                                           private_key=private_key))
#         # Очищаем состояние после добавления кошелька
#         await state.clear()
#         # Отправляем сообщение с предложением продолжить и клавиатурой основного меню
#         await message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)
#     except Exception as e:
#         detailed_error_traceback = traceback.format_exc()
#         logger.error(f"Error in process_wallet_description: {e}\n{detailed_error_traceback}")


@create_wallet_router.message(StateFilter(FSMWallet.create_wallet_add_description))
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
        await message.answer(text=LEXICON["create_description_wallet"], reply_markup=back_keyboard)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_invalid_wallet_description: {e}\n{detailed_error_traceback}")
