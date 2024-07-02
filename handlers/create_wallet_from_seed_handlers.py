# solana_wallet_telegram_bot/handlers/create_wallet_handlers.py

import traceback

import mnemonic
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from solders.keypair import Keypair

from applications.wallet.models import Wallet
from keyboards.back_keyboard import back_keyboard
from keyboards.return_main_keyboard import return_main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from services.wallet_service import create_wallet, get_user
from states.states import FSMWallet
from utils.qr_utils import get_photo_qr_code
from utils.validators import is_valid_wallet_name, is_valid_wallet_description, is_valid_wallet_seed_phrase

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
# def create_wallet(user, name, description, wallet_address, solana_derivation_path):
#     wallet = Wallet.objects.create(
#         wallet_address=wallet_address,
#         name=name,
#         description=description,
#         solana_derivation_path=solana_derivation_path,
#     )
#     if wallet:
#         wallet.user.set([user])
#         user.last_solana_derivation_path = solana_derivation_path
#         user.save()
#     return wallet
########################################################################################################################

# Telegram
########################################################################################################################
# Инициализируем роутер уровня модуля
create_wallet_from_seed_router: Router = Router()


########################################################################################################################
@create_wallet_from_seed_router.callback_query(F.data == "callback_button_create_wallet_from_seed",
                                               StateFilter(FSMWallet.create_wallet_method_chosen))
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
        # Отправляем сообщение с просьбой ввести seed фразу для кошелька
        await callback.message.edit_text(LEXICON["create_seed_wallet"], reply_markup=back_keyboard)
        await state.set_state(FSMWallet.create_wallet_from_seed_add_seed)
        # Избегаем ощущения, что бот завис и избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_create_wallet_from_seed_command: {error}\n{detailed_send_message_error}")


########################################################################################################################

@create_wallet_from_seed_router.message(StateFilter(FSMWallet.create_wallet_from_seed_add_seed),
                                        lambda message: message.text and is_valid_wallet_seed_phrase(message.text))
async def process_wallet_seed(message: Message, state: FSMContext) -> None:
    """
        Handler for entering the wallet seed phrase.

        Args:
            message (Message): The incoming message.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        seed_phrase = message.text

        await state.update_data(seed_phrase=seed_phrase)

        # Получаем данные из состояния
        data = await state.get_data()

        # Извлекаем seed фразу из данных
        seed_phrase = data.get("seed_phrase")

        # Отправляем подтверждение с введенной seed фразой
        await message.answer(text=LEXICON["wallet_seed_confirmation"].format(seed_phrase=seed_phrase))

        # Запрашиваем ввод описания кошелька
        await message.answer(text=LEXICON["create_name_wallet"], reply_markup=back_keyboard)

        # Переходим к добавлению описания кошелька
        await state.set_state(FSMWallet.create_wallet_from_seed_add_name)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_wallet_seed: {e}\n{detailed_error_traceback}")


@create_wallet_from_seed_router.message(StateFilter(FSMWallet.create_wallet_from_seed_add_seed))
async def process_invalid_wallet_seed(message: Message, state: FSMContext) -> None:
    """
        Handler for incorrect wallet seed input.

        Args:
            message (Message): The incoming message.
            state (FSMContext): The state of the finite state machine.

        Returns:
            None
    """
    try:
        # Отправляем сообщение о некорректной seed фразе
        await message.answer(text=LEXICON["invalid_wallet_seed"])

        # Запрашиваем ввод имени кошелька заново
        await message.answer(text=LEXICON["create_seed_wallet"], reply_markup=back_keyboard)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_invalid_wallet_seed: {e}\n{detailed_error_traceback}")


########################################################################################################################

@create_wallet_from_seed_router.message(StateFilter(FSMWallet.create_wallet_from_seed_add_name),
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
        await state.set_state(FSMWallet.create_wallet_from_seed_add_description)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_wallet_name: {e}\n{detailed_error_traceback}")


@create_wallet_from_seed_router.message(StateFilter(FSMWallet.create_wallet_from_seed_add_name))
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


########################################################################################################################

@create_wallet_from_seed_router.message(StateFilter(FSMWallet.create_wallet_from_seed_add_description),
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
        await state.update_data(description=message.text)
        data = await state.get_data()
        seed_phrase = data.get("seed_phrase")
        name = data.get("wallet_name")
        description = data.get("description")

        user = await get_user(telegram_id=message.from_user.id)

        user_wallets = []

        async for w in Wallet.objects.filter(user=user):
            user_wallets.append(w.wallet_address)

        # last_number_solana_derivation_path = 0

        # # если int значит уже была запись в user.last_number_solana_derivation_path
        # if isinstance(user.last_number_solana_derivation_path, int):
        #     last_number_solana_derivation_path = user.last_number_solana_derivation_path + 1
        if user.last_solana_derivation_path:
            derivation_path = user.last_solana_derivation_path
            derivation_path_list = derivation_path.split('/')
            last_el = derivation_path_list[-1]
            index = int(last_el[0]) + 1

        while True:
            solana_derivation_path = f"m/44'/501'/0'/{index}'"

            mnemo = mnemonic.Mnemonic("english")
            seed = mnemo.to_seed(seed_phrase, passphrase="")
            keypair = Keypair.from_seed_and_derivation_path(seed, solana_derivation_path)
            wallet_address = str(keypair.pubkey())
            private_key = keypair.secret().hex()

            if wallet_address not in user_wallets:
                break
            else:
                index += 1

        wallet = await create_wallet(
            user=user,
            name=name,
            description=description,
            wallet_address=wallet_address,
            solana_derivation_path=solana_derivation_path,
        )

        if wallet:
            await state.update_data(sender_address=wallet.wallet_address, sender_private_key=private_key)

        # Если адреса кошелька нет, выводим сообщение об успешном создании и возвращаемся в главное меню
        await message.answer(
            LEXICON["wallet_created_successfully"].format(wallet_name=wallet.name,
                                                          wallet_description=wallet.description,
                                                          wallet_address=wallet.wallet_address,
                                                          private_key=private_key,
                                                          seed_phrase=seed_phrase))
        # Создаем QR-код и получаем его картинку
        photo = await get_photo_qr_code(wallet)
        # Отправляем сообщение с изображением QR-кода
        await message.answer_photo(photo=photo, caption=LEXICON["qr_code_caption"], reply_markup=return_main_keyboard)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_wallet_description: {e}\n{detailed_error_traceback}")


@create_wallet_from_seed_router.message(StateFilter(FSMWallet.create_wallet_from_seed_add_description))
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
########################################################################################################################
