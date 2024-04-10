# solana-webwallet/handlers/transfer_handlers.py

import asyncio
import traceback
from decimal import Decimal

import solana.rpc.core
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from config_data.config import LAMPORT_TO_SOL_RATIO
from database.database import get_db
from external_services.solana.solana import (
    is_valid_wallet_address,
    is_valid_private_key,
    is_valid_amount,
    get_sol_balance,
    http_client,
    transfer_token,
    get_wallet_address_from_private_key,
)
from keyboards.back_keyboard import back_keyboard
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from models.models import SolanaWallet
from states.states import FSMWallet

# Инициализируем роутер уровня модуля
transfer_router: Router = Router()


@transfer_router.callback_query(F.data.startswith("wallet_address:"),
                                StateFilter(FSMWallet.transfer_choose_sender_wallet))
async def process_choose_sender_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the user's selection of the sender wallet for transfer.

        Args:
            callback (CallbackQuery): The callback query object containing data about the selected wallet.
            state (FSMContext): The state context for working with chat states.

        Returns:
            None
    """
    try:
        # Извлекаем адрес кошелька из callback_data
        wallet_address = callback.data.split(":")[1]

        # Асинхронно получаем доступ к базе данных.
        async with await get_db() as session:
            # Получаем данные кошелька из базы данных по его адресу
            wallet = await session.execute(select(SolanaWallet).filter_by(wallet_address=wallet_address))
            wallet = wallet.scalar()

            # # Обновляем данные состояния с адресом и приватным ключом отправителя
            # await state.update_data(sender_address=wallet.wallet_address, sender_private_key=wallet.private_key)
            # Обновляем данные состояния с адресом отправителя
            await state.update_data(sender_address=wallet.wallet_address)

        # Отправляем запрос на ввод адреса получателя
        await callback.message.edit_text(LEXICON["transfer_sender_private_key_prompt"], reply_markup=back_keyboard)
        # Устанавливаем состояние transfer_recipient_address для перехода к следующему шагу в процессе перевода.
        # await state.set_state(FSMWallet.transfer_recipient_address)
        await state.set_state(FSMWallet.transfer_sender_private_key)
        # Избегаем ощущения, что бот завис, избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_choose_sender_wallet: {e}\n{detailed_error_traceback}")


@transfer_router.message(StateFilter(FSMWallet.transfer_sender_private_key))
async def process_transfer_sender_private_key(message: Message, state: FSMContext) -> None:
    """
        Handles the user input of the sender's private key.

        Args:
            message (Message): The user message containing the sender's private key.
            state (FSMContext): The state context for managing chat states.

        Returns:
            None
    """
    try:
        private_key = message.text
        if is_valid_private_key(private_key):
            data = await state.get_data()
            sender_address_from_bd = data.get("sender_address")
            sender_address_from_keypair = get_wallet_address_from_private_key(private_key)
            if sender_address_from_bd == sender_address_from_keypair:
                # Обновляем данные состояния с приватным ключом отправителя
                await state.update_data(sender_private_key=private_key)
                # Отправляем запрос на ввод адреса получателя
                await message.answer(LEXICON["transfer_recipient_address_prompt"], reply_markup=back_keyboard)
                # Устанавливаем состояние transfer_recipient_address для перехода к следующему шагу в процессе перевода.
                await state.set_state(FSMWallet.transfer_recipient_address)
            else:
                sent_message = await message.answer(LEXICON["invalid_private_key"], reply_markup=None)
                await asyncio.sleep(1)
                await message.delete()
                await sent_message.delete()
                await message.answer(LEXICON["transfer_sender_private_key_prompt"], reply_markup=back_keyboard)
                # или
                # await message.answer(LEXICON["invalid_private_key"])
                # await message.answer(LEXICON["transfer_sender_private_key_prompt"], reply_markup=back_keyboard)
        else:
            sent_message = await message.answer(LEXICON["invalid_private_key"], reply_markup=None)
            await asyncio.sleep(1)
            await message.delete()
            await sent_message.delete()
            await message.answer(LEXICON["transfer_sender_private_key_prompt"], reply_markup=back_keyboard)
            # или
            # await message.answer(LEXICON["invalid_private_key"])
            # await message.answer(LEXICON["transfer_sender_private_key_prompt"], reply_markup=back_keyboard)

    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_transfer_sender_private_key: {e}\n{detailed_error_traceback}")


@transfer_router.message(StateFilter(FSMWallet.transfer_recipient_address))
async def process_transfer_recipient_address(message: Message, state: FSMContext) -> None:
    """
        Handles the input of the recipient address for the transfer.

        Args:
            message (Message): The message object containing the recipient address entered by the user.
            state (FSMContext): The state context for working with chat states.

        Raises:
            Exception: If an error occurs while processing the request.

        Returns:
            None
    """
    try:
        # Извлекаем текст сообщения, который содержит адрес получателя, из объекта message.
        recipient_address = message.text

        # Проверяем валидность введенного адреса получателя.
        if is_valid_wallet_address(recipient_address):
            # Если адрес получателя валиден, обновляем данные состояния.
            await state.update_data(recipient_address=recipient_address)
            # Отправляем запрос на ввод суммы для перевода.
            await message.answer(LEXICON["transfer_amount_prompt"], reply_markup=None)
            # Устанавливаем состояние transfer_amount для перехода к следующему шагу в процессе перевода.
            await state.set_state(FSMWallet.transfer_amount)
        else:
            # Если адрес получателя невалиден, отправляем сообщение с просьбой ввести корректный адрес.
            sent_message = await message.answer(LEXICON["invalid_wallet_address"], reply_markup=None)
            await asyncio.sleep(1)
            await message.delete()
            await sent_message.delete()
            await message.answer(LEXICON["transfer_recipient_address_prompt"], reply_markup=back_keyboard)
            # или
            # await message.answer(LEXICON["invalid_wallet_address"])
            # await message.answer(LEXICON["transfer_recipient_address_prompt"], reply_markup=back_keyboard)
    except Exception as error:
        # Обработка и логирование ошибок, возникших во время обработки запроса.
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_transfer_recipient_address: {error}\n{detailed_error_traceback}")


@transfer_router.message(StateFilter(FSMWallet.transfer_amount))
async def process_transfer_amount(message: Message, state: FSMContext) -> None:
    """
        Handles the user's input of the transfer amount in the transfer process.

        Args:
            message (Message): The message object containing the amount entered by the user.
            state (FSMContext): The state context for working with chat states.

        Raises:
            Exception: If an error occurs while processing the request.

        Returns:
            None
    """
    try:
        # Преобразуем текст сообщения, содержащий сумму перевода, в строку, чтобы можно было заменить запятые на точки,
        # если они присутствуют.
        amount_text = str(message.text).replace(',', '.')
        if not is_valid_amount(amount_text):
            raise ValueError

        amount = float(amount_text)
        # Получаем данные из состояния чата.
        data = await state.get_data()
        # Извлекаем адрес отправителя из данных состояния.
        sender_address = data.get("sender_address")
        # Извлекаем приватный ключ отправителя из данных состояния.
        sender_private_key = data.get("sender_private_key")
        # Извлекаем адрес получателя из данных состояния.
        recipient_address = data.get("recipient_address")

        try:
            # Пытаемся получить текущий баланс отправителя.
            balance = await get_sol_balance(sender_address, http_client)
            # Запрашиваем минимальный баланс для аренды освобождения.
            # Аргумент функции - размер данных в байтах, для которых требуется выделить место в памяти.
            # min_balance_resp = http_client.get_minimum_balance_for_rent_exemption(1)
            min_balance_resp = (await http_client.get_minimum_balance_for_rent_exemption(1)).value
            # Извлекаем значение минимального баланса из ответа. Min balance: 897840lamports/1000000000 = 0.00089784 Sol
            min_balance = min_balance_resp / LAMPORT_TO_SOL_RATIO
            logger.debug(f"Balance: {balance}, Min balance: {min_balance}")

        # В случае возникновения ошибки при получении баланса отправителя или минимального баланса.
        except Exception as error:
            detailed_error_traceback = traceback.format_exc()
            logger.error(f"Error getting Solana balance or minimum balance: {error}\n{detailed_error_traceback}")

            # Отправляем пользователю сообщение о недостаточном балансе и запрос на ввод суммы для перевода.
            sent_message = await message.answer(LEXICON["insufficient_balance"], reply_markup=None)
            await asyncio.sleep(1)
            await message.delete()
            await sent_message.delete()
            await message.answer(LEXICON["transfer_amount_prompt"], reply_markup=back_keyboard)
            # или
            # await message.answer(LEXICON["insufficient_balance"])
            # await message.answer(LEXICON["transfer_amount_prompt"])

            # Возвращаемся из функции, чтобы предотвратить дальнейшее выполнение кода.
            return

        # Если баланс отправителя достаточен для перевода (включая минимальный баланс).
        if balance >= amount + min_balance:
            # Выполняем перевод токенов.
            result = await transfer_token(sender_address, sender_private_key, recipient_address, amount, http_client)
            # Если перевод выполнен успешно, отправляем сообщение об успешном переводе.
            if result:
                # formatted_amount = '{:.6f}'.format(amount)
                formatted_amount = '{:.6f}'.format(Decimal(str(amount)))
                await message.answer(
                    LEXICON["transfer_successful"].format(amount=formatted_amount, recipient=recipient_address))
            # Если перевод не выполнен успешно, отправляем сообщение о неудаче.
            else:
                await message.answer(
                    LEXICON["transfer_not_successful"].format(amount=amount, recipient=recipient_address))

        # Если баланс отправителя недостаточен для перевода (включая минимальный баланс).
        else:
            # Отправляем пользователю сообщение о недостаточном балансе и запрос на ввод суммы для перевода.
            sent_message = await message.answer(LEXICON["insufficient_balance"], reply_markup=None)
            await asyncio.sleep(1)
            await message.delete()
            await sent_message.delete()
            await message.answer(LEXICON["transfer_amount_prompt"], reply_markup=back_keyboard)
            # или
            # await message.answer(LEXICON["insufficient_balance"])
            # await message.answer(LEXICON["transfer_amount_prompt"])
            # Выходим из функции после вывода сообщений
            return

        # Очищаем состояние перед завершением.
        await state.clear()
        # Отправляем сообщение с инструкцией о продолжении и клавиатурой основных кнопок.
        await message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)

    # Если возникает ошибка типа ValueError, когда пользователь вводит некорректную сумму.
    except ValueError:
        # Отправляем сообщение о неверной сумме и просим пользователя ввести сумму для перевода заново.
        sent_message = await message.answer(LEXICON["invalid_amount"], reply_markup=None)
        await asyncio.sleep(1)
        await message.delete()
        await sent_message.delete()
        await message.answer(LEXICON["transfer_amount_prompt"])
    except solana.rpc.core.RPCException as rpc_exception:
        # Проверяем, является ли ошибка связанной с недостаточным балансом для аренды.
        if "InsufficientFundsForRent" in str(rpc_exception):
            # Отправляем сообщение пользователю о нехватке баланса для аренды.
            sent_message = await message.answer(LEXICON["insufficient_balance_recipient"], reply_markup=None)
            await asyncio.sleep(1)
            await message.delete()
            await sent_message.delete()
            await message.answer(LEXICON["transfer_recipient_address_prompt"])
            # Устанавливаем состояние transfer_recipient_address для возврата к запросу адреса получателя.
            await state.set_state(FSMWallet.transfer_recipient_address)
        else:
            logger.error(f"Error during token transfer: {rpc_exception}")
            await message.answer("An error occurred during the token transfer. Please try again later.")
