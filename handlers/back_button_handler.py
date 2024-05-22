# solana_wallet_telegram_bot/handlers/back_button_handler.py

import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.back_keyboard import back_keyboard
from keyboards.return_main_keyboard import return_main_keyboard
from keyboards.transfer_transaction_keyboards import get_wallet_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from services.wallet_service import retrieve_user_wallets
from states.states import FSMWallet

back_button_router = Router()


@back_button_router.callback_query(F.data == "callback_button_back", StateFilter(FSMWallet))
async def process_back_button(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        # Получаем текущее состояние из контекста состояния конечного автомата
        current_state = await state.get_state()
        #############################################################################################################

        # Если текущее состояние - добавление описания нового кошелька
        if current_state == FSMWallet.create_wallet_add_description:
            await state.set_state(FSMWallet.create_wallet_add_name)
            await callback.message.edit_text(LEXICON["create_new_name_wallet"], reply_markup=return_main_keyboard)
        #############################################################################################################

        # Если текущее состояние - добавление имени для подключения кошелька
        elif current_state == FSMWallet.connect_wallet_add_name:
            await state.set_state(FSMWallet.connect_wallet_add_address)
            await callback.message.edit_text(LEXICON["connect_wallet_address"], reply_markup=back_keyboard)
        ################################################################################################################

        # Если текущее состояние - добавление описания для подключения кошелька
        elif current_state == FSMWallet.connect_wallet_add_description:
            await state.set_state(FSMWallet.connect_wallet_add_name)
            await callback.message.edit_text(LEXICON["connect_wallet_add_name"], reply_markup=back_keyboard)
        ################################################################################################################

        # Если текущее состояние - ввод приватного ключа отправителя для трансфера
        elif current_state == FSMWallet.transfer_sender_private_key:
            await state.set_state(FSMWallet.transfer_choose_sender_wallet)
            await callback.message.edit_text(LEXICON["list_sender_wallets"])
            # Получаем пользователя и его кошельки
            _, user_wallets = await retrieve_user_wallets(callback)
            wallet_keyboard = await get_wallet_keyboard(user_wallets)
            await callback.message.edit_reply_markup(reply_markup=wallet_keyboard)
        ################################################################################################################

        # Если текущее состояние - ввод адреса получателя для трансфера
        elif current_state == FSMWallet.transfer_recipient_address:
            await state.set_state(FSMWallet.transfer_sender_private_key)
            await callback.message.edit_text(LEXICON["transfer_sender_private_key_prompt"], reply_markup=back_keyboard)
        ################################################################################################################

        # Если текущее состояние - ввод суммы для трансфера
        elif current_state == FSMWallet.transfer_amount:
            await state.set_state(FSMWallet.transfer_recipient_address)
            await callback.message.edit_text(LEXICON["transfer_recipient_address_prompt"], reply_markup=back_keyboard)
        ################################################################################################################

        # Отправляем ответ на запрос обратного вызова для подтверждения обработки
        await callback.answer()
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_back_button: {e}\n{detailed_error_traceback}")
