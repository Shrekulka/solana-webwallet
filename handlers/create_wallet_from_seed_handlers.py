# solana_wallet_telegram_bot/handlers/create_wallet_handlers.py

import mnemonic
import traceback

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
# from sqlalchemy import select
from solders.keypair import Keypair
from web3 import Web3, AsyncWeb3
from eth_account import Account

# from database.database import get_db
from config_data.config import CURRENT_BLOCKCHAIN
from keyboards.back_keyboard import back_keyboard
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from states.states import FSMWallet
from utils.validators import is_valid_wallet_name, is_valid_wallet_description, is_valid_wallet_seed_phrase

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
def create_wallet(user, name, description, wallet_address, derivation_path, blockchain):
    print("****** blockchain:", blockchain)
    if blockchain == 'bsc':
        blockchain_choices = Blockchain.BINANCE_SMART_CHAIN
        user.last_bsc_derivation_path = derivation_path
        user.save()

    elif blockchain == 'solana':
        blockchain_choices = Blockchain.SOLANA
        user.last_solana_derivation_path = derivation_path
        user.save()

    wallet = Wallet.objects.create(
        wallet_address=wallet_address,
        name=name,
        description=description,
        blockchain=blockchain_choices,
        derivation_path=derivation_path,
    )

    if wallet:
        wallet.user.set([user])

    return wallet

############################

# Инициализируем роутер уровня модуля
create_wallet_from_seed_router: Router = Router()


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
        index = 0
        blockchain = CURRENT_BLOCKCHAIN

        user = await get_user(telegram_id=message.from_user.id)

        user_wallets = []

        async for w in Wallet.objects.filter(user=user):
            user_wallets.append(w.wallet_address)

        if blockchain == 'solana':
            if user.last_solana_derivation_path:
                derivation_path = user.last_solana_derivation_path
                list_from_derivation_path = derivation_path.split('/')
                last_el = list_from_derivation_path[-1]
                index = int(last_el[0]) + 1

            while True:
                derivation_path = f"m/44'/501'/0'/{index}'"

                mnemo = mnemonic.Mnemonic("english")
                seed = mnemo.to_seed(seed_phrase, passphrase="")
                keypair = Keypair.from_seed_and_derivation_path(seed, derivation_path)
                wallet_address = str(keypair.pubkey())
                private_key = keypair.secret().hex()

                if wallet_address not in user_wallets:
                    break
                else:
                    index += 1

        if blockchain == 'bsc':
            if user.last_bsc_derivation_path:
                derivation_path = user.last_bsc_derivation_path
                list_from_derivation_path = derivation_path.split('/')
                last_el = list_from_derivation_path[-1]
                index = int(last_el[0]) + 1

            w3 = AsyncWeb3()
            # The use of the Mnemonic features of Account is disabled by default until its API stabilizes.
            # To use these features, please enable them by running `Account.enable_unaudited_hdwallet_features()` and try again.
            Account.enable_unaudited_hdwallet_features()
            #TODO: BNB 24-word mnemonic and derivation path: https://docs.bnbchain.org/docs/learn/genesis/
            # we use 12-word

            while True:
                derivation_path = f"m/44'/60'/0'/0/{index}"

                acct = Account.from_mnemonic(
                    mnemonic=seed_phrase,
                    passphrase='',
                    account_path=derivation_path,
                )

                wallet_address = acct.address
                private_key = w3.to_hex(acct.key)

                if wallet_address not in user_wallets:
                    break
                else:
                    index += 1

        wallet = await create_wallet(
            user=user,
            name=name,
            description=description,
            wallet_address=wallet_address,
            derivation_path=derivation_path,
            blockchain=blockchain,
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
        # Очищаем состояние после добавления кошелька
        await state.clear()
        # Отправляем сообщение с предложением продолжить и клавиатурой основного меню
        await message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)
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
