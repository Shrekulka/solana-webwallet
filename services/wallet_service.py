# solana_wallet_telegram_bot/services/wallet_service.py
import asyncio
import json
import traceback
from decimal import Decimal
from typing import Tuple, Optional, List

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message
from aiogram.types import User
from asgiref.sync import sync_to_async

from applications.wallet.models import Transaction
from applications.wallet.models import Wallet
from config_data.config import LAMPORT_TO_SOL_RATIO
from config_data.config import SOLANA_DERIVATION_PATH
# from database.database import get_db
from external_services.solana.solana import get_sol_balance, http_client, is_valid_wallet_address
from keyboards.back_keyboard import back_keyboard
from keyboards.connect_wallet import connect_wallet_keyboard
from keyboards.main_keyboard import main_keyboard
from keyboards.return_main_keyboard import return_main_keyboard
from keyboards.transfer_transaction_keyboards import get_wallet_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from services.user_service import get_user
from states.states import FSMWallet
from utils.qr_utils import get_photo_qr_code
from utils.validators import is_valid_wallet_name, is_valid_wallet_description


########### django #########


# from sqlalchemy import select


#
# @sync_to_async
# def get_user(telegram_id):
#     # DjangoUser = get_user_model()
#     user = User.objects.filter(telegram_id=telegram_id).first()
#     return user
#
# ############################


async def retrieve_user_wallets(callback: CallbackQuery) -> Tuple[Optional[User], List[Wallet]]:
    """
        Retrieves user wallets from the database.
        This function retrieves a user's wallets from the database based on their Telegram ID provided in the callback.

        Args:
            callback (CallbackQuery): The callback query object containing information about the user who sent the
            request.

        Returns:
            Tuple[Optional[User], List[Wallet]]: A tuple containing the user (if it exists) and a list of their wallets.

        Raises:
            None
    """

    # Получаем пользователя по его ID в Telegram
    user = await get_user(telegram_id=callback.from_user.id)
    # Инициализация переменной для списка кошельков пользователя
    user_wallets = []
    # Проверяем, если пользователь существует
    if user:
        # Получаем кошельки пользователя из базы данных
        async for w in Wallet.objects.filter(user=user):
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


async def format_transaction_message(transaction) -> str:
    """
        Formats transaction information for user-friendly display.

        Args:
            transaction: Transaction object containing information about the transaction made.

        Returns:
            str: Formatted transaction message ready to be sent to the user.

        Raises:
            None
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


async def format_transaction_from_db_message(transaction) -> str:
    """
        Formats transaction information from the database for user-friendly display.

        Args:
            transaction: Transaction object from the database.

        Returns:
            str: Formatted transaction message from the database.

        Raises:
            None
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


async def check_wallet_exists(user: User, wallet_address: str) -> bool:
    """
        Checks if a user has a wallet with the given address.

        Args:
            user (User): The user.
            wallet_address (str): The wallet address to check.

        Returns:
            bool: True if the user has a wallet with the specified address, otherwise False.

        Raises:
            None
    """
    # Создаем список для хранения адресов кошельков пользователя
    user_wallets = []
    # Итерируемся по всем кошелькам пользователя из базы данных
    async for w in Wallet.objects.filter(user=user):
        # Добавляем адреса кошельков в список
        user_wallets.append(w.wallet_address)

    # Проверяем, содержится ли указанный адрес кошелька в списке пользовательских кошельков
    return wallet_address in user_wallets


async def check_wallet_name_exists(user: User, wallet_name: str) -> bool:
    """
        Checks if a wallet with the specified name exists for the user.

        Args:
            user (User): The user.
            wallet_name (str): The name of the wallet to check.

        Returns:
            bool: True if a wallet with the specified name exists for the user, otherwise False.

        Raises:
            None
    """
    # Создаем список для хранения имен кошельков пользователя
    user_names = []
    # Итерируемся по всем кошелькам пользователя из базы данных
    async for w in Wallet.objects.filter(user=user):
        # Добавляем имена кошельков в список
        user_names.append(w.name)

    # Проверяем, содержится ли указанное имя кошелька в списке имен пользовательских кошельков
    return wallet_name in user_names


async def handle_wallet_error(message: Message, state: FSMContext, target_state: State, wallet_info: str,
                              error_type: str) -> None:
    """
        Handles errors related to wallet information input.

        This function is intended to handle errors that occur when the user inputs wallet information,
        such as wallet address, wallet name, and wallet description. Depending on the error type (`error_type`),
        the function reacts accordingly:

        - If the error is related to an invalid or existing wallet address (`invalid_wallet_address` or
          `existing_wallet_address`), the function sends an error message, deletes it after one second, returns the user
           to the wallet address input state, and requests wallet address input again.

        - If the error is related to an invalid or existing wallet name (`invalid_wallet_name` or
          `existing_wallet_name`), the function sends an error message, deletes it after one second, returns the user to
           the wallet name input state, and requests wallet name input again.

        - If the error is related to an invalid wallet description (`invalid_wallet_description`),
          the function sends an error message, deletes it after one second, returns the user to the wallet description
          input state, and requests wallet description input again.

        - If an unknown error occurs, the function sends a general error message and returns the user to the default
          state.

        In case an exception occurs while handling the error, the function logs detailed error information
        and sends the user an error processing message.

        Args:
            message (Message): The message object containing the wallet information that caused the error.
            state (FSMContext): The FSM context object for state management.
            target_state (State): The FSM state to which the user should be returned after error handling.
            wallet_info (str): Information about the wallet associated with the error (address, name, or description).
            error_type (str): The type of error, determining how to handle it.

        Returns:
            None
    """
    try:
        # 1) Если ошибка связана с неверным или уже существующим адресом кошелька
        ################################################################################################################
        if error_type in ["invalid_wallet_address", "existing_wallet_address"]:
            if error_type == "invalid_wallet_address":
                # Если адрес неверен, отправляем сообщение об ошибке и удаляем его через 1 секунду
                sent_message = await message.reply(LEXICON["invalid_wallet_address"].format(wallet_address=wallet_info))
                await asyncio.sleep(1)
                await sent_message.delete()
            elif error_type == "existing_wallet_address":
                # Если адрес уже существует, отправляем сообщение об ошибке и удаляем его через 1 секунду
                sent_message = await message.reply(
                    LEXICON["this_wallet_already_exists"].format(wallet_address=wallet_info))
                await asyncio.sleep(1)
                await sent_message.delete()

            await state.set_state(target_state)
            current_state = await state.get_state()

            if current_state == FSMWallet.connect_wallet_method_chosen:
                await message.answer(LEXICON["choose_wallet_connection_method"], reply_markup=connect_wallet_keyboard)
            else:
                # Возвращаем пользователя к вводу адреса кошелька
                await message.answer(LEXICON["connect_wallet_add_address"], reply_markup=back_keyboard)
        # 2) Если ошибка связана с неверным или уже существующим именем кошелька
        ################################################################################################################
        elif error_type in ["invalid_wallet_name", "existing_wallet_name"]:
            if error_type == "invalid_wallet_name":
                # Если имя неверно, отправляем сообщение об ошибке и удаляем его через 1 секунду
                sent_message = await message.reply(LEXICON["invalid_wallet_name"].format(wallet_name=wallet_info))
                await asyncio.sleep(1)
                await sent_message.delete()

            elif error_type == "existing_wallet_name":
                # Если имя уже существует, отправляем сообщение об ошибке и удаляем его через 1 секунду
                sent_message = await message.reply(
                    LEXICON["this_wallet_name_already_exists"].format(wallet_name=wallet_info))
                await asyncio.sleep(1)
                await sent_message.delete()

            # Возвращаем пользователя к вводу имени кошелька
            await state.set_state(target_state)
            await message.answer(LEXICON["create_name_wallet"], reply_markup=back_keyboard)
        # 3) Если ошибка связана с неверным описанием кошелька
        ################################################################################################################
        elif error_type == "invalid_wallet_description":
            sent_message = await message.reply(
                LEXICON["invalid_wallet_description"].format(wallet_description=wallet_info))
            await asyncio.sleep(1)
            await sent_message.delete()
            # Возвращаем пользователя к вводу описания кошелька
            await state.set_state(target_state)
            await message.answer(LEXICON["create_description_wallet"], reply_markup=back_keyboard)
        # 4) Если произошла неизвестная ошибка, отправляем сообщение об ошибке и возвращаемся к состоянию по умолчанию
        ################################################################################################################
        else:
            await message.reply(LEXICON["error_message"])
            await state.set_state(FSMWallet.default_state)
    except Exception as e:
        # Если произошла ошибка в обработке ошибки, записываем ее в лог и отправляем пользователю сообщение об ошибке
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in handle_wallet_error: {e}\n{detailed_error_traceback}")
        await message.reply(LEXICON["processing_error"])


async def handle_wallet_name_input(message: Message, state: FSMContext, is_connect: bool) -> None:
    """
        Handles the user input for a wallet name.

        This function saves the entered wallet name to the state, checks its validity
        and existence for the user. If the name is valid and does not exist, the function
        requests a wallet description from the user and transitions to the next FSM state.
        If the name is invalid or already exists, the function handles the error and requests
        the wallet name again.

        Args:
            message (Message): The message object containing the entered wallet name.
            state (FSMContext): The FSM context object for state management.
            is_connect (bool): A flag indicating whether the operation is to connect an existing
                wallet or to create a new one.

        Returns:
            None
    """
    try:
        # Сохраняем введенное имя кошелька в состояние
        await state.update_data(name=message.text)

        # Получаем данные из состояния
        state_data = await state.get_data()

        # Извлекаем имя кошелька из данных
        wallet_name = state_data.get("name")

        # Проверяем валидность имени кошелька
        if is_valid_wallet_name(wallet_name):
            # Получаем пользователя по его ID в Telegram
            user = await get_user(telegram_id=message.from_user.id)

            # Проверяем, существует ли уже кошелек с таким именем у пользователя
            if await check_wallet_name_exists(user, wallet_name):
                # Обрабатываем ошибку, если кошелек с таким именем уже существует
                await handle_wallet_error(message, state,
                                          FSMWallet.create_wallet_constructor_command_add_name if not is_connect
                                          else FSMWallet.connect_wallet_constructor_command_add_name,
                                          wallet_name, "existing_wallet_name")
            else:
                # Обновляем данные состояния, добавляя имя кошелька
                await state.update_data(wallet_name=wallet_name)

                # Отправляем подтверждение с введенным именем кошелька
                await message.answer(text=LEXICON["wallet_name_confirmation"].format(wallet_name=wallet_name))

                # Запрашиваем ввод описания кошелька
                await message.answer(text=LEXICON["create_description_wallet"], reply_markup=back_keyboard)

                # Устанавливаем новое состояние для добавления описания кошелька
                await state.set_state(
                    FSMWallet.create_wallet_constructor_command_add_description if not is_connect
                    else FSMWallet.connect_wallet_constructor_command_add_description)
        else:
            # Если имя невалидно, обрабатываем ошибку и просим ввести имя заново
            await handle_wallet_error(message, state,
                                      FSMWallet.create_wallet_constructor_command_add_name if not is_connect
                                      else FSMWallet.connect_wallet_constructor_command_add_name,
                                      wallet_name, "invalid_wallet_name")

    except Exception as e:
        # Записываем информацию об ошибке в лог
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in handle_wallet_name_input: {e}\n{detailed_error_traceback}")

        # Возвращаем пользователя в состояние ввода имени кошелька и выводим сообщение об ошибке
        await state.set_state(
            FSMWallet.create_wallet_constructor_command_add_name if not is_connect
            else FSMWallet.connect_wallet_constructor_command_add_name)
        await message.reply(LEXICON["error_message"])
        await message.answer(LEXICON["create_name_wallet"], reply_markup=back_keyboard)


async def handle_wallet_address(message: Message, state: FSMContext, wallet_data: dict) -> bool:
    if 'wallet_address' in wallet_data:
        wallet_address = wallet_data['wallet_address']
        if is_valid_wallet_address(wallet_address):
            logger.info("Wallet address is valid")
            user = await get_user(telegram_id=message.from_user.id)
            if await check_wallet_exists(user, wallet_address):
                logger.info("Wallet is exist")
                await handle_wallet_error(message, state, FSMWallet.connect_wallet_method_chosen,
                                          wallet_address, "existing_wallet_address")
                return False  # Возвращаем False, если кошелек уже существует
            else:
                logger.info("Wallet isn't exist")
                await state.update_data(wallet_address=wallet_address)
                return True  # Возвращаем True, если адрес валиден и кошелек не существует
        else:
            logger.info("Wallet address isn't valid")
            await handle_wallet_error(message, state, FSMWallet.connect_wallet_qr_add_code,
                                      wallet_address, "invalid_wallet_address")
            return False  # Возвращаем False, если адрес невалиден
    else:
        await message.answer(LEXICON["error_message"])
        return False  # Возвращаем False, если нет адреса кошелька

    return False  # Возвращаем False по умолчанию


# async def handle_wallet_name(message: Message, state: FSMContext, wallet_data: dict) -> bool:
#     if 'wallet_name' in wallet_data:
#         wallet_name = wallet_data['wallet_name']
#         if is_valid_wallet_name(wallet_name):
#             logger.info("Wallet address is valid")
#             user = await get_user(telegram_id=message.from_user.id)
#             if await check_wallet_name_exists(user, wallet_name):
#                 logger.info("Wallet name is exist")
#                 await handle_wallet_error(message, state, FSMWallet.connect_wallet_method_chosen,
#                                           wallet_name, "existing_wallet_address")
#                 return False  # Возвращаем False, если имя кошелька уже существует
#             else:
#                 logger.info("Wallet isn't exist")
#                 await state.update_data(name=wallet_name)
#                 return True  # Возвращаем True, если адрес валиден и кошелек не существует
#         else:
#             await handle_wallet_error(message, state, FSMWallet.connect_wallet_qr_add_code,
#                                       wallet_name, "invalid_wallet_name")
#             return False
#     else:
#         await handle_wallet_name_input(message, state, is_connect=True)
#         return False


async def handle_wallet_description(message: Message, state: FSMContext, wallet_data: dict) -> bool:
    if 'wallet_description' in wallet_data:
        wallet_description = wallet_data['wallet_description']
        if is_valid_wallet_description(wallet_description):
            await state.update_data(description=wallet_description)

            state_data = await state.get_data()
            wallet_name = state_data.get("name")
            wallet_address = state_data.get("wallet_address")

            user = await get_user(telegram_id=message.from_user.id)
            wallet = await create_wallet(user=user, wallet_address=wallet_address, name=wallet_name,
                                         description=wallet_description)

            if wallet:
                await message.answer(
                    LEXICON["wallet_connected_successfully"].format(name=wallet.name,
                                                                    description=wallet.description,
                                                                    wallet_address=wallet.wallet_address, ))

                photo = await get_photo_qr_code(wallet)
                await message.answer_photo(photo=photo, caption=LEXICON["qr_code_caption"],
                                           reply_markup=return_main_keyboard)
            return True
        else:
            await handle_wallet_error(message, state, FSMWallet.connect_wallet_qr_add_code,
                                      wallet_description, "invalid_wallet_description")
            return False
    else:
        await message.answer(LEXICON["create_description_wallet"], reply_markup=back_keyboard)
        await state.set_state(FSMWallet.connect_wallet_qr_add_description)
        return False


@sync_to_async
def create_wallet(user: User, wallet_address: str, name: str, description: str,
                  solana_derivation_path: str = SOLANA_DERIVATION_PATH) -> Wallet:
    """
        Asynchronously creates a wallet for the user with the specified parameters.

        Args:
            user (User): The user object to whom the wallet belongs.
            wallet_address (str): The wallet address.
            name (str): The name of the wallet.
            description (str): The description of the wallet.
            solana_derivation_path (str, optional): The derivation path for Solana. Default is SOLANA_DERIVATION_PATH.

        Returns:
            Wallet: The created wallet object.

        Raises:
            None
    """
    # Создаем кошелек в базе данных
    wallet = Wallet.objects.create(
        wallet_address=wallet_address,
        name=name,
        description=description,
        solana_derivation_path=solana_derivation_path,
    )
    # Привязываем кошелек к пользователю
    if wallet:
        wallet.user.set([user])
        user.last_solana_derivation_path = solana_derivation_path
        user.save()
    return wallet


@sync_to_async
def delete_wallet(user: User, wallet_address: str):
    """
        Asynchronously deletes a user's wallet with the specified address.

        Args:
            user (User): The user object to whom the wallet belongs.
            wallet_address (str): The wallet address to delete.

        Returns:
            int: The number of objects deleted.

        Raises:
            None
    """
    wallet = Wallet.objects.filter(user=user, wallet_address=wallet_address).first()
    if wallet:
        wallet.transactions.all().delete()  # Удалить все связанные транзакции
        number_objects_deleted = wallet.delete()
        return number_objects_deleted
    return 0


@sync_to_async
def get_wallet(wallet_address: str):
    """
        Asynchronously retrieves a wallet object based on its address.

        Args:
            wallet_address (str): The wallet address.

        Returns:
            Wallet: The wallet object if found, otherwise None.

        Raises:
            None
    """
    # Получаем кошелек по его адресу из базы данных
    wallet = Wallet.objects.filter(wallet_address=wallet_address).first()
    return wallet


@sync_to_async
def update_wallet(wallet_address: str, solana_derivation_path: str):
    """
        Asynchronously updates the derivation path for the wallet with the specified address.

        Args:
            wallet_address (str): The wallet address to update.
            solana_derivation_path (str): The new derivation path for Solana.

        Returns:
            Wallet: The updated wallet object.

        Raises:
            None
    """
    # Находим кошелек по его адресу в базе данных и обновляем путь производной
    wallet = Wallet.objects.filter(wallet_address=wallet_address).first()
    wallet.solana_derivation_path = solana_derivation_path
    wallet.save()
    return wallet


@sync_to_async
def get_transaction_history_from_db(wallet_address: str):
    """
        Asynchronously retrieves transaction history from the database for the wallet with the specified address.

        Args:
            wallet_address (str): The wallet address.

        Returns:
            List[Transaction]: A list of transaction objects for the wallet if found, otherwise an empty list.

        Raises:
            None
    """
    # Получаем объект кошелька по его адресу из базы данных
    wallet = Wallet.objects.filter(wallet_address=wallet_address).first()
    transaction_history_from_db = []
    # Если кошелек найден, получаем историю его транзакций
    if wallet:
        transaction_history_from_db = wallet.transactions.all().order_by('-transaction_time')
    return transaction_history_from_db


@sync_to_async
def save_transaction(tr: Transaction) -> Optional[None]:
    """
        Asynchronously saves transaction information to the database.

        Args:
            tr (Transaction): The transaction object to save.

        Returns:
            Optional[None]: Does not return anything.

        Raises:
            None
    """
    # Инициализация списка адресов для кошельков
    address_list = []
    # Инициализация переменной для кошельков
    wallets = None
    # Преобразование объекта транзакции в словарь
    tr_dict = json.loads(tr.to_json())

    # Извлечение данных о транзакции из словаря
    transaction_id = tr_dict['transaction']['signatures'][0] or ''
    sender = tr_dict['transaction']['message']['accountKeys'][0] or ''
    recipient = tr_dict['transaction']['message']['accountKeys'][1] or ''
    slot = tr_dict['slot'] or None
    transaction_time = tr_dict['blockTime'] or None
    transaction_status = f"{tr_dict['meta']['status'] or ''}"
    transaction_err = f"{tr_dict['meta']['err'] or ''}"
    pre_balances = tr_dict['meta']['preBalances'][0] or None
    post_balances = tr_dict['meta']['postBalances'][0] or None

    # Добавление отправителя и получателя в список адресов
    if sender:
        address_list.append(sender)
    if recipient:
        address_list.append(recipient)

    # Получение кошельков по списку адресов
    if address_list:
        wallets = Wallet.objects.filter(wallet_address__in=address_list)

    # Если найдены кошельки и идентификатор транзакции существует
    if wallets and transaction_id:
        # Проверяем, существует ли уже объект транзакции в базе данных
        transaction_obj = Transaction.objects.filter(transaction_id=transaction_id).first()

        if transaction_obj:
            # Если транзакция существует, обновляем связанные с ней кошельки
            transaction_obj.wallet.set(wallets)
        else:
            try:
                # Создаем новый объект транзакции и связываем его с кошельками
                create_transaction_obj = Transaction.objects.create(
                    transaction_id=transaction_id,
                    slot=slot,
                    transaction_time=transaction_time,
                    sender=sender,
                    recipient=recipient,
                    pre_balances=pre_balances,
                    post_balances=post_balances,
                    transaction_status=transaction_status,
                    transaction_err=transaction_err,
                )
                create_transaction_obj.wallet.set(wallets)
            except Exception as er:
                print(f'Error create transaction: {er}')

    return None
