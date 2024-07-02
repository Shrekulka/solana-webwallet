# solana_wallet_telegram_bot/handlers/connect_wallet_handlers.py
import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from external_services.solana.solana import is_valid_wallet_address
from keyboards.back_keyboard import back_keyboard
from keyboards.main_keyboard import main_keyboard
from keyboards.return_main_keyboard import return_main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from services.wallet_service import get_user, create_wallet, check_wallet_exists, handle_wallet_error, \
    handle_wallet_name_input
from states.states import FSMWallet
from utils.qr_utils import get_photo_qr_code
from utils.validators import is_valid_wallet_description

# Django
########################################################################################################################
# @sync_to_async
# def get_user(telegram_id):
#     User = get_user_model()
#     user = User.objects.filter(telegram_id=telegram_id).first()
#     return user
#
#
# @sync_to_async
# def create_wallet(user, wallet_address, name, description):
#     wallet = Wallet.objects.create(
#         wallet_address=wallet_address,
#         name=name,
#         description=description,
#     )
#     wallet.user.set([user])
#     return wallet
########################################################################################################################

# Telegram
########################################################################################################################

# Инициализируем роутер уровня модуля
connect_wallet_constructor_command_router: Router = Router()


@connect_wallet_constructor_command_router.callback_query(F.data == "callback_button_connect_wallet_constructor",
                                                          StateFilter(FSMWallet.connect_wallet_method_chosen))
async def process_connect_wallet_command(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the initial wallet connection command from the user.

        This function is triggered when the user clicks the "Connect Wallet" button and is in the state where
        they have chosen a wallet connection method. It prompts the user to enter their wallet address and
        transitions to the appropriate state for address input.

        Args:
            callback (CallbackQuery): The callback query object containing data about the user's interaction with
                                      the bot.
            state (FSMContext): The current state of the finite state machine, used for managing user states
                                across multiple steps.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the process, it logs the error and resets the user's state to
                       the default state.
    """
    try:
        # Запрашиваем у пользователя адрес кошелька
        await callback.message.edit_text(LEXICON["connect_wallet_add_address"], reply_markup=back_keyboard)
        # Переход в состояние добавления
        await state.set_state(FSMWallet.connect_wallet_constructor_command_add_address)
        # Избегаем ощущения, что бот завис и избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_connect_wallet_command: {error}\n{detailed_send_message_error}")
        # Возвращаем пользователя в состояние по умолчанию и выводим сообщение об ошибке
        await state.set_state(FSMWallet.default_state)
        await callback.answer(LEXICON["error_message"], reply_markup=main_keyboard)


@connect_wallet_constructor_command_router.message(
    StateFilter(FSMWallet.connect_wallet_constructor_command_add_address))
async def process_connect_wallet_address(message: Message, state: FSMContext) -> None:
    """
        Handles the input of the wallet address during the wallet connection process.

        This function is triggered when the user inputs their wallet address while in the state of adding
        the wallet address. It validates the wallet address, checks if the address is already associated
        with the user, and then updates the state to request the wallet name if the address is valid.

        Args:
            message (Message): The incoming message object containing the user's input.
            state (FSMContext): The current state of the finite state machine, used for managing user states
                                across multiple steps.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the process, it logs the error, resets the state to request
                       the wallet address again, and sends an error message to the user.
    """
    try:
        # Извлекаем адрес кошелька из текста сообщения
        wallet_address = message.text

        # Проверяем валидность адреса кошелька
        if is_valid_wallet_address(wallet_address):
            # Получаем пользователя по его ID в Telegram
            user = await get_user(telegram_id=message.from_user.id)

            # Проверяем, существует ли уже кошелек с таким адресом у пользователя
            if await check_wallet_exists(user, wallet_address):
                # Обрабатываем ошибку, если кошелек уже существует
                await handle_wallet_error(message, state, FSMWallet.connect_wallet_constructor_command_add_address,
                                          wallet_address, "existing_wallet_address")
            else:
                # Обновляем данные состояния, добавляя адрес кошелька
                await state.update_data(wallet_address=wallet_address)
                # Отправляем запрос на ввод имени кошелька
                await message.answer(LEXICON["create_name_wallet"], reply_markup=back_keyboard)
                # Устанавливаем новое состояние для добавления имени кошелька
                await state.set_state(FSMWallet.connect_wallet_constructor_command_add_name)
        else:
            # Если адрес невалиден, отправляем сообщение об ошибке и просим ввести адрес заново
            await handle_wallet_error(message, state, FSMWallet.connect_wallet_constructor_command_add_address,
                                      wallet_address, "invalid_wallet_address")
    except Exception as e:
        # Обработка ошибок и запись подробной информации в лог
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_connect_wallet_address: {e}\n{detailed_error_traceback}")
        # Возвращаем пользователя в состояние ввода адреса кошелька и выводим сообщение об ошибке
        await state.set_state(FSMWallet.connect_wallet_constructor_command_add_address)
        await message.reply(LEXICON["error_message"])
        await message.answer(LEXICON["connect_wallet_add_address"], reply_markup=back_keyboard)


@connect_wallet_constructor_command_router.message(StateFilter(FSMWallet.connect_wallet_constructor_command_add_name))
async def process_connect_wallet_name(message: Message, state: FSMContext) -> None:
    """
        Handles the input of a wallet name when connecting an existing wallet.

        Args:
            message (Message): The message object containing the entered wallet name.
            state (FSMContext): The FSM context object for state management.

        Returns:
            None: This function does not return anything explicitly.

        Notes:
            is_connect (bool): A flag indicating whether the operation is to connect an existing wallet (True)
            or to create a new wallet (False). This affects the choice of the next FSM state and error handling.
    """
    # Эта строка вызывает функцию handle_wallet_name_input для обработки введенного имени кошелька.
    # Параметр message содержит информацию о сообщении, включая введенное имя кошелька.
    # Параметр state представляет объект контекста FSM для управления состояниями.
    # Параметр is_connect установлен в True, что указывает на то, что это операция подключения существующего кошелька.
    await handle_wallet_name_input(message, state, is_connect=True)


# @connect_wallet_constructor_command_router.message(StateFilter(FSMWallet.connect_wallet_constructor_command_add_name))
# async def process_connect_wallet_name(message: Message, state: FSMContext) -> None:
#     """
#         Handles the input of the wallet name during the wallet connection process.
#
#         This function is triggered when the user inputs the wallet name while in the state of adding the
#         wallet name. It validates the wallet name, checks if the name is already associated with the user,
#         and then updates the state to request the wallet description if the name is valid.
#
#         Args:
#             message (Message): The incoming message object containing the user's input.
#             state (FSMContext): The current state of the finite state machine, used for managing user states
#                                 across multiple steps.
#
#         Returns:
#             None
#
#         Raises:
#             Exception: If an error occurs during the process, it logs the error, resets the state to request
#                        the wallet name again, and sends an error message to the user.
#     """
#     try:
#         # Сохраняем введенное имя кошелька в состояние
#         await state.update_data(name=message.text)
#
#         # Получаем данные из состояния
#         state_data = await state.get_data()
#
#         # Извлекаем имя кошелька из данных
#         wallet_name = state_data.get("name")
#
#         # Проверяем валидность имени кошелька
#         if is_valid_wallet_name(wallet_name):
#             # Получаем пользователя по его ID в Telegram
#             user = await get_user(telegram_id=message.from_user.id)
#
#             # Проверяем, существует ли уже кошелек с таким именем у пользователя
#             if await check_wallet_name_exists(user, wallet_name):
#                 # Обрабатываем ошибку, если кошелек с таким именем уже существует
#                 await handle_wallet_error(message, state, FSMWallet.connect_wallet_constructor_command_add_name,
#                                           wallet_name, "existing_wallet_name")
#             else:
#                 # Обновляем данные состояния, добавляя имя кошелька
#                 await state.update_data(wallet_name=wallet_name)
#                 # Отправляем подтверждение с введенным именем кошелька
#                 await message.answer(text=LEXICON["wallet_name_confirmation"].format(wallet_name=wallet_name))
#                 # Запрашиваем ввод описания кошелька
#                 await message.answer(text=LEXICON["create_description_wallet"], reply_markup=back_keyboard)
#                 # Устанавливаем новое состояние для добавления описания кошелька
#                 await state.set_state(FSMWallet.connect_wallet_constructor_command_add_description)
#         else:
#             # Если имя невалидно, обрабатываем ошибку и просим ввести имя заново
#             await handle_wallet_error(message, state, FSMWallet.connect_wallet_constructor_command_add_name,
#                                       wallet_name, "invalid_wallet_name")
#
#     except Exception as e:
#         detailed_error_traceback = traceback.format_exc()
#         logger.error(f"Error in process_connect_wallet_name: {e}\n{detailed_error_traceback}")
#         # Возвращаем пользователя в состояние ввода имени кошелька и выводим сообщение об ошибке
#         await state.set_state(FSMWallet.connect_wallet_constructor_command_add_name)
#         await message.reply(LEXICON["error_message"])
#         await message.answer(LEXICON["create_name_wallet"], reply_markup=back_keyboard)


@connect_wallet_constructor_command_router.message(
    StateFilter(FSMWallet.connect_wallet_constructor_command_add_description))
async def process_connect_wallet_description(message: Message, state: FSMContext) -> None:
    """
        Handles the input of the wallet description during the wallet connection process.

        This function is triggered when the user inputs the wallet description while in the state of adding the
        wallet description. It validates the description, creates the wallet, and sends a confirmation message
        along with a QR code if the description is valid.

        Args:
            message (Message): The incoming message object containing the user's input.
            state (FSMContext): The current state of the finite state machine, used for managing user states
                                across multiple steps.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the process, it logs the error, resets the state to request
                       the wallet description again, and sends an error message to the user.
    """
    try:
        # Извлекаем описание кошелька из сообщения
        wallet_description = message.text

        # Проверяем валидность описания кошелька
        if is_valid_wallet_description(wallet_description):
            # Обновляем данные состояния, добавляя введенное описание
            await state.update_data(description=wallet_description)
            # Получаем данные из состояния
            state_data = await state.get_data()
            # Извлекаем имя кошелька из данных состояния
            wallet_name = state_data.get("name")
            # Извлекаем адрес кошелька из данных (если он есть)
            wallet_address = state_data.get("wallet_address")
            # Получаем пользователя по его ID в Telegram
            user = await get_user(telegram_id=message.from_user.id)
            # Создаем кошелек с данными пользователя, адресом, именем и описанием кошелька
            wallet = await create_wallet(user=user, wallet_address=wallet_address, name=wallet_name,
                                         description=wallet_description)
            # Если кошелек успешно создан
            if wallet:
                # Отправляем сообщение об успешном подключении
                await message.answer(
                    LEXICON["wallet_connected_successfully"].format(name=wallet.name,
                                                                    description=wallet.description,
                                                                    wallet_address=wallet.wallet_address, ))

                # Создаем QR-код для кошелька и получаем его изображение
                photo = await get_photo_qr_code(wallet)
                # Отправляем сообщение с изображением QR-кода и кнопкой возврата в главное меню
                await message.answer_photo(photo=photo, caption=LEXICON["qr_code_caption"],
                                           reply_markup=return_main_keyboard)
        else:
            # Если описание невалидно, отправляем сообщение об ошибке и просим ввести описание заново
            await handle_wallet_error(message, state, FSMWallet.connect_wallet_constructor_command_add_description,
                                      wallet_description, "invalid_wallet_description")

    except Exception as e:
        # Обработка ошибок и запись подробной информации в лог
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_connect_wallet_description: {e}\n{detailed_error_traceback}")
        # Возвращаем пользователя в состояние ввода описания кошелька и выводим сообщение об ошибке
        await state.set_state(FSMWallet.connect_wallet_constructor_command_add_description)
        await message.reply(LEXICON["error_message"])
        await message.answer(LEXICON["create_description_wallet"], reply_markup=back_keyboard)
