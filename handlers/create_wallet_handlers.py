# solana_wallet_telegram_bot/handlers/create_wallet_handlers.py
import traceback

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.database import get_db
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from models.models import SolanaWallet
from states.states import FSMWallet
from utils.validators import is_valid_wallet_name, is_valid_wallet_description

# Инициализируем роутер уровня модуля
create_wallet_router: Router = Router()


@create_wallet_router.message(StateFilter(FSMWallet.add_name_wallet),
                              lambda message: is_valid_wallet_name(message.text))
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
        # Логируем информацию о сообщении
        logger.info(message.model_dump_json(indent=4, exclude_none=True))

        # Сохраняем введенное имя кошелька в состояние
        await state.update_data(wallet_name=message.text)

        # Получаем данные из состояния
        data = await state.get_data()

        # Извлекаем имя кошелька из данных
        name = data.get("wallet_name")

        # Отправляем подтверждение с введенным именем кошелька
        await message.answer(text=LEXICON["wallet_name_confirmation"].format(wallet_name=name))

        # Запрашиваем ввод описания кошелька
        await message.answer(text=LEXICON["wallet_description_prompt"])

        # Переходим к добавлению описания кошелька
        await state.set_state(FSMWallet.add_description_wallet)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_wallet_name: {e}\n{detailed_error_traceback}")


@create_wallet_router.message(StateFilter(FSMWallet.add_name_wallet))
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
        await message.answer(text=LEXICON["wallet_name_prompt"])
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_invalid_wallet_name: {e}\n{detailed_error_traceback}")


@create_wallet_router.message(StateFilter(FSMWallet.add_description_wallet),
                              lambda message: is_valid_wallet_description(message.text))
async def process_wallet_description(message: Message, state: FSMContext) -> None:
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
            # Если wallet_address есть в данных состояния, обновляем существующий кошелек
            if wallet_address:
                wallet = await SolanaWallet.update_wallet(session, message.from_user.id, wallet_address, name=name,
                                                          description=description)
                if wallet is None:  # Если кошелек не найден, создаем новый
                    wallet = await SolanaWallet.wallet_create(session, message.from_user.id, name=name,
                                                              description=description)
                    await state.update_data(sender_address=wallet.wallet_address, sender_private_key=wallet.private_key)
            # Иначе создаем новый кошелек
            else:
                wallet = await SolanaWallet.wallet_create(session, message.from_user.id, name=name,
                                                          description=description)
                await state.update_data(sender_address=wallet.wallet_address, sender_private_key=wallet.private_key)

        # Если в данных состояния есть адрес кошелька
        if wallet_address:
            # Обновляем данные состояния с адресом и приватным ключом отправителя
            await state.update_data(sender_address=wallet.wallet_address,
                                    sender_private_key=wallet.private_key)
            # Отправка запроса на ввод адреса получателя
            await message.answer(LEXICON["transfer_recipient_address_prompt"])
            # Установка состояния ввода адреса получателя
            await state.set_state(FSMWallet.transfer_recipient_address)
        else:
            # Если адреса кошелька нет, выводим сообщение об успешном создании и возвращаемся в главное меню
            await message.answer(
                LEXICON["wallet_created_successfully"].format(wallet_name=wallet.name,
                                                              wallet_description=wallet.description,
                                                              wallet_address=wallet.wallet_address,
                                                              private_key=wallet.private_key))
            # Очищаем состояние после добавления кошелька
            await state.clear()
            # Отправляем сообщение с предложением продолжить и клавиатурой основного меню
            await message.answer(LEXICON["continue_message"], reply_markup=main_keyboard)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_wallet_description: {e}\n{detailed_error_traceback}")


# @create_wallet_router.message(StateFilter(FSMWallet.add_description_wallet),
#                               lambda message: is_valid_wallet_description(message.text))
# async def process_wallet_description(message: Message, state: FSMContext) -> None:
#     """
#         Handler for entering the wallet description.
#
#         Args:
#             message (Message): The incoming message.
#             state (FSMContext): The state of the finite state machine.
#
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
#         # Создаем соединение с базой данных
#         async with await get_db() as session:
#             # Создаем кошелек в базе данных
#             wallet = await SolanaWallet.wallet_create(session, message.from_user.id, name=name,
#                                                       description=description)
#         # Отправляем сообщение об успешном создании кошелька
#         await message.answer(
#             LEXICON["wallet_created_successfully"].format(wallet_name=wallet.name,
#                                                           wallet_description=wallet.description,
#                                                           wallet_address=wallet.wallet_address,
#                                                           private_key=wallet.private_key))
#         # Очищаем состояние после добавления кошелька
#         await state.clear()
#         # Отправляем сообщение с предложением продолжить и клавиатурой основного меню
#         await message.answer(LEXICON["continue_message"], reply_markup=main_keyboard)
#     except Exception as e:
#         detailed_error_traceback = traceback.format_exc()
#         logger.error(f"Error in process_wallet_description: {e}\n{detailed_error_traceback}")


@create_wallet_router.message(StateFilter(FSMWallet.add_description_wallet))
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
