# solana_wallet_telegram_bot/handlers/transfer_handlers.py
import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from database.database import get_db
from external_services.solana.solana import is_valid_wallet_address, get_sol_balance, http_client, transfer_token
from keyboards.transfer_keyboards import transfer_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from models.models import SolanaWallet, User
from states.states import FSMWallet

# Инициализируем роутер уровня модуля
transfer_router: Router = Router()


# Обработчик сообщения с состоянием FSMWallet.choose_sender_wallet
@transfer_router.message(StateFilter(FSMWallet.choose_sender_wallet))
async def process_choose_sender_wallet(message: Message, state: FSMContext) -> None:
    try:
        user_wallets = []
        # Получение доступа к базе данных
        async with await get_db() as session:
            # Получение кошельков пользователя из базы данных
            user = await session.execute(select(User).filter_by(telegram_id=message.from_user.id))
            user = user.scalar()

            if user:
                user_wallets = await session.execute(select(SolanaWallet).filter_by(user_id=user.id))
                user_wallets = user_wallets.scalars().all()

        # Создание словаря для хранения опций кошельков
        wallet_options = {f"{wallet.name} ({wallet.wallet_address})": wallet for wallet in user_wallets}

        # Если введенный текст является адресом кошелька
        if is_valid_wallet_address(message.text) and user_wallets:
            # Проверяем, есть ли такой адрес в базе
            selected_wallet = next((wallet for wallet in user_wallets if wallet.wallet_address == message.text), None)
            if selected_wallet:
                # Обновление данных состояния с адресом и приватным ключом отправителя
                await state.update_data(sender_address=selected_wallet.wallet_address,
                                        sender_private_key=selected_wallet.private_key)
                # Отправка запроса на ввод адреса получателя
                await message.answer(LEXICON["transfer_recipient_address_prompt"])
                # Установка состояния ввода адреса получателя
                await state.set_state(FSMWallet.transfer_recipient_address)
            else:
                await message.answer(LEXICON["save_new_wallet_prompt"], reply_markup=transfer_keyboard)
                await state.update_data(new_wallet_address=message.text)
                await state.set_state(FSMWallet.confirm_save_new_wallet)
        else:
            # Если введен неверный адрес кошелька, отправляем сообщение об ошибке
            await message.answer(LEXICON["invalid_wallet_choice"])
            # Запрос на повторный выбор отправителя
            await message.answer(LEXICON["choose_sender_wallet"])
    except Exception as e:
        # Обработка и логирование ошибки
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_choose_sender_wallet: {e}\n{detailed_error_traceback}")


# Обработчик подтверждения сохранения нового кошелька
@transfer_router.callback_query(F.data == "callback_button_save_wallet", StateFilter(FSMWallet.confirm_save_new_wallet))
async def confirm_save_new_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        data = await state.get_data()
        new_wallet_address = data.get("new_wallet_address")

        # Скрытие клавиатуры
        await callback.message.edit_reply_markup(reply_markup=None)
        # Запрашиваем имя кошелька
        await callback.message.answer(LEXICON["wallet_name_prompt"])
        await state.set_state(FSMWallet.add_name_wallet)
        await state.update_data(wallet_address=new_wallet_address)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in confirm_save_new_wallet: {e}\n{detailed_error_traceback}")


# Обработчик отмены сохранения нового кошелька
@transfer_router.callback_query(F.data == "callback_button_cancel", StateFilter(FSMWallet.confirm_save_new_wallet))
async def cancel_save_new_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(LEXICON["transfer_recipient_address_prompt"])
        await state.set_state(FSMWallet.transfer_recipient_address)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in cancel_save_new_wallet: {e}\n{detailed_error_traceback}")


@transfer_router.message(StateFilter(FSMWallet.transfer_recipient_address))
async def process_transfer_recipient_address(message: Message, state: FSMContext) -> None:
    try:
        recipient_address = message.text

        if is_valid_wallet_address(recipient_address):
            await state.update_data(recipient_address=recipient_address)
            await message.answer(LEXICON["transfer_amount_prompt"])
            await state.set_state(FSMWallet.transfer_amount)
        else:
            await message.answer(LEXICON["invalid_wallet_address"])
            await message.answer(LEXICON["transfer_recipient_address_prompt"])
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_transfer_recipient_address: {e}\n{detailed_error_traceback}")


@transfer_router.message(StateFilter(FSMWallet.transfer_amount))
async def process_transfer_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = float(message.text)
        data = await state.get_data()
        sender_address = data.get("sender_address")
        sender_private_key = data.get("sender_private_key")
        recipient_address = data.get("recipient_address")

        balance = await get_sol_balance(sender_address, http_client)

        logger.debug(f"Sender_address: {sender_address}, recipient_address: {recipient_address}, balance: {balance}, amount: {amount}")

        if balance >= amount:
            result = await transfer_token(sender_address, sender_private_key, recipient_address, amount, http_client)
            if result:
                await message.answer(LEXICON["transfer_successful"].format(amount=amount, recipient=recipient_address))
            else:
                await message.answer(LEXICON["transfer_not_successful"].format(amount=amount, recipient=recipient_address))
        else:
            await message.answer(LEXICON["insufficient_balance"])
            await message.answer(LEXICON["transfer_amount_prompt"])

        await state.clear()
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_transfer_amount: {e}\n{detailed_error_traceback}")