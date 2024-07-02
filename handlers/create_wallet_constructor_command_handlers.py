# solana_wallet_telegram_bot/handlers/create_wallet_constructor_command_handlers.py
import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config_data.config import SOLANA_DERIVATION_PATH
from external_services.solana.solana import create_solana_wallet
from keyboards.back_keyboard import back_keyboard
from keyboards.return_main_keyboard import return_main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from services.wallet_service import get_user, create_wallet, handle_wallet_error, \
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
create_wallet_constructor_command_router: Router = Router()


########################################################################################################################
@create_wallet_constructor_command_router.callback_query(F.data == "callback_button_create_wallet_constructor",
                                                         StateFilter(FSMWallet.create_wallet_method_chosen))
async def process_create_wallet_command(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        # Отправляем сообщение с просьбой ввести имя для кошелька
        await callback.message.edit_text(LEXICON["create_name_wallet"], reply_markup=back_keyboard)
        # Переход в состояние добавления имени кошелька
        await state.set_state(FSMWallet.create_wallet_constructor_command_add_name)
        # Избегаем ощущения, что бот завис и избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_create_wallet_command: {error}\n{detailed_send_message_error}")


@create_wallet_constructor_command_router.message(StateFilter(FSMWallet.create_wallet_constructor_command_add_name))
async def create_wallet_name_handler(message: Message, state: FSMContext) -> None:
    """
        Handles the input of a wallet name when creating a new wallet.

        Args:
            message (Message): The message object containing the entered wallet name.
            state (FSMContext): The FSM context object for state management.

        Returns:
            Optional[None]: This function does not return anything explicitly.

        Notes:
            is_connect (bool): A flag indicating whether the operation is to connect an existing wallet (True)
            or to create a new wallet (False). This affects the choice of the next FSM state and error handling.
    """
    # Эта строка вызывает функцию handle_wallet_name_input для обработки введенного имени кошелька.
    # Параметр message содержит информацию о сообщении, включая введенное имя кошелька.
    # Параметр state представляет объект контекста FSM для управления состояниями.
    # Параметр is_connect установлен в False, так как это операция создания нового кошелька, а не подключение
    # существующего.
    await handle_wallet_name_input(message, state, is_connect=False)


# @create_wallet_constructor_command_router.message(StateFilter(FSMWallet.create_wallet_constructor_command_add_name))
# async def process_create_wallet_name(message: Message, state: FSMContext) -> None:
#     try:
#         # Сохраняем введенное имя кошелька в состояние
#         await state.update_data(name=message.text)
#
#         # Получаем данные из состояния
#         data = await state.get_data()
#
#         # Извлекаем имя кошелька из данных
#         wallet_name = data.get("name")
#
#         # Проверяем валидность имени кошелька
#         if is_valid_wallet_name(wallet_name):
#             # Получаем пользователя по его ID в Telegram
#             user = await get_user(telegram_id=message.from_user.id)
#
#             # Проверяем, существует ли уже кошелек с таким именем у пользователя
#             if await check_wallet_name_exists(user, wallet_name):
#                 # Обрабатываем ошибку, если кошелек с таким именем уже существует
#                 await handle_wallet_error(message, state, FSMWallet.create_wallet_constructor_command_add_name,
#                                           wallet_name, "existing_wallet_name")
#             else:
#                 # Обновляем данные состояния, добавляя имя кошелька
#                 await state.update_data(wallet_name=wallet_name)
#                 # Отправляем подтверждение с введенным именем кошелька
#                 await message.answer(text=LEXICON["wallet_name_confirmation"].format(wallet_name=wallet_name))
#                 # Запрашиваем ввод описания кошелька
#                 await message.answer(text=LEXICON["create_description_wallet"], reply_markup=back_keyboard)
#                 # Устанавливаем новое состояние для добавления описания кошелька
#                 await state.set_state(FSMWallet.create_wallet_constructor_command_add_description)
#         else:
#             # Если имя невалидно, обрабатываем ошибку и просим ввести имя заново
#             await handle_wallet_error(message, state, FSMWallet.create_wallet_constructor_command_add_name,
#                                       wallet_name, "invalid_wallet_name")
#
#     except Exception as e:
#         detailed_error_traceback = traceback.format_exc()
#         logger.error(f"Error in process_create_wallet_name: {e}\n{detailed_error_traceback}")
#         # Возвращаем пользователя в состояние ввода имени кошелька и выводим сообщение об ошибке
#         await state.set_state(FSMWallet.connect_wallet_constructor_command_add_name)
#         await message.reply(LEXICON["error_message"])
#         await message.answer(LEXICON["create_name_wallet"], reply_markup=back_keyboard)


@create_wallet_constructor_command_router.message(
    StateFilter(FSMWallet.create_wallet_constructor_command_add_description))
async def process_create_wallet_description(message: Message, state: FSMContext):
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
            wallet_address, private_key, seed_phrase = await create_solana_wallet()
            wallet = await create_wallet(
                user=user,
                wallet_address=wallet_address,
                name=wallet_name,
                description=wallet_description,
                solana_derivation_path=SOLANA_DERIVATION_PATH,
            )
            if wallet:
                await state.update_data(sender_address=wallet.wallet_address, sender_private_key=private_key)

            # Если адреса кошелька нет, выводим сообщение об успешном создании и возвращаемся в главное меню
            await message.answer(
                LEXICON["wallet_created_successfully"].format(name=wallet.name,
                                                              description=wallet.description,
                                                              wallet_address=wallet.wallet_address,
                                                              private_key=private_key,
                                                              seed_phrase=seed_phrase))
            # Создаем QR-код и получаем его картинку
            photo = await get_photo_qr_code(wallet)

            # Отправляем сообщение с изображением QR-кода
            await message.answer_photo(photo=photo, caption=LEXICON["qr_code_caption"],
                                       reply_markup=return_main_keyboard)
        else:
            # Если описание невалидно, отправляем сообщение об ошибке и просим ввести описание заново
            await handle_wallet_error(message, state, FSMWallet.create_wallet_constructor_command_add_description,
                                      wallet_description, "invalid_wallet_description")

    except Exception as e:
        # Обработка ошибок и запись подробной информации в лог
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_create_wallet_description: {e}\n{detailed_error_traceback}")
        # Возвращаем пользователя в состояние ввода описания кошелька и выводим сообщение об ошибке
        await state.set_state(FSMWallet.create_wallet_constructor_command_add_description)
        await message.reply(LEXICON["error_message"])
        await message.answer(LEXICON["invalid_wallet_description"], reply_markup=back_keyboard)
