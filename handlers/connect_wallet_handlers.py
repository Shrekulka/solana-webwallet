# solana_wallet_telegram_bot/handlers/connect_wallet_handlers.py
import traceback

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.database import get_db
from external_services.solana.solana import is_valid_wallet_address, get_wallet_address_from_private_key
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from models.models import SolanaWallet
from states.states import FSMWallet

# Инициализируем роутер уровня модуля
connect_wallet_router: Router = Router()


@connect_wallet_router.message(StateFilter(FSMWallet.connect_wallet_address))
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
            await state.update_data(wallet_address=wallet_address)
            # Отправляем запрос на ввод приватного ключа
            await message.answer(LEXICON["connect_wallet_private_key_prompt"])
            # Устанавливаем состояние для ввода приватного ключа
            await state.set_state(FSMWallet.connect_wallet_private_key)
        else:
            # Если адрес невалиден, отправляем сообщение об ошибке и просим ввести адрес заново
            await message.answer(LEXICON["invalid_wallet_address"])
            await message.answer(LEXICON["connect_wallet_address_prompt"])
    except Exception as e:
        # Обработка ошибок и запись подробной информации в лог
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_connect_wallet_address: {e}\n{detailed_error_traceback}")


# @connect_wallet_router.message(StateFilter(FSMWallet.connect_wallet_address),
#                                lambda message: not is_valid_wallet_address(message.text))
# async def process_invalid_wallet_address(message: Message, state: FSMContext) -> None:
#     """
#         Handler for incorrect wallet address input.
#
#         Args:
#             message (Message): The incoming message.
#             state (FSMContext): The state of the finite state machine.
#
#         Returns:
#             None
#     """
#     try:
#         # Отправляем сообщение об ошибке
#         await message.answer(text=LEXICON["invalid_wallet_address"])
#         # Запрашиваем адрес кошелька еще раз
#         await message.answer(text=LEXICON["connect_wallet_address_prompt"])
#     except Exception as e:
#         detailed_error_traceback = traceback.format_exc()
#         logger.error(f"Error in process_invalid_wallet_address: {e}\n{detailed_error_traceback}")


@connect_wallet_router.message(StateFilter(FSMWallet.connect_wallet_private_key))
async def process_connect_wallet_private_key(message: Message, state: FSMContext) -> None:
    """
        Handler for entering the wallet's private key for connection.

        Args:
            message (Message): The incoming message.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        # Извлекаем введенный пользователем приватный ключ из текста сообщения
        private_key = message.text

        # Получаем данные из состояния, которые были сохранены на предыдущем этапе
        data = await state.get_data()

        # Извлекаем адрес кошелька из данных состояния по ключу "wallet_address"
        wallet_address = data.get("wallet_address")

        # Получаем адрес кошелька, вычисленный из введенного пользователем приватного ключа
        derived_wallet_address = get_wallet_address_from_private_key(private_key)

        # Проверяем, соответствует ли вычисленный адрес сохраненному адресу кошелька
        if derived_wallet_address == wallet_address:
            # Если адреса совпадают, устанавливаем соединение с кошельком в базе данных
            async with await get_db() as session:
                wallet = await SolanaWallet.connect_wallet(session, message.from_user.id, wallet_address, private_key)
            # Отправляем сообщение об успешном подключении кошелька и очищаем состояние
            await message.answer(
                LEXICON["wallet_connected_successfully"].format(wallet_address=wallet.wallet_address),
                reply_markup=main_keyboard)
            await state.clear()
        else:
            # Если адреса не совпадают, отправляем сообщение об ошибке и просим ввести приватный ключ заново
            await message.answer(LEXICON["invalid_private_key"])
            await message.answer(LEXICON["connect_wallet_private_key_prompt"])
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_connect_wallet_private_key: {e}\n{detailed_error_traceback}")

#
# @connect_wallet_router.message(StateFilter(FSMWallet.connect_wallet_private_key),
#                                lambda message: not is_valid_private_key(message.text))
# async def process_invalid_private_key(message: Message, state: FSMContext) -> None:
#     """
#         Handler for incorrect wallet's private key input.
#
#         Args:
#             message (Message): The incoming message.
#             state (FSMContext): The state of the finite state machine.
#
#         Returns:
#             None
#     """
#     try:
#         # Отправляем сообщение об ошибке и просим ввести приватный ключ заново
#         await message.answer(text=LEXICON["invalid_private_key"])
#         await message.answer(text=LEXICON["connect_wallet_private_key_prompt"])
#     except Exception as e:
#         detailed_error_traceback = traceback.format_exc()
#         logger.error(f"Error in process_invalid_private_key: {e}\n{detailed_error_traceback}")
