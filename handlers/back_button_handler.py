# solana_wallet_telegram_bot/handlers/back_button_handler.py

import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery

from config_data.config import CURRENT_BLOCKCHAIN
from keyboards.back_keyboard import back_keyboard
from keyboards.main_keyboard import main_keyboard
from keyboards.transfer_transaction_keyboards import get_wallet_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from services.wallet_service import retrieve_user_wallets
from states.states import FSMWallet

back_button_router = Router()


@back_button_router.callback_query(F.data == "callback_button_back", StateFilter(FSMWallet))
async def process_back_button(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the "Back" button press during interaction with the bot.

        Arguments:
        callback (CallbackQuery): The callback query object.
        state (FSMContext): The state context of the finite state machine.

        Returns:
        None
    """
    try:
        # Получаем текущее состояние из контекста состояния конечного автомата
        current_state = await state.get_state()

        # Если текущее состояние - добавление имени нового кошелька
        if current_state == FSMWallet.create_wallet_add_name:
            await state.set_state(default_state)
            await callback.message.edit_text(LEXICON["back_to_main_menu"])
            await callback.message.edit_reply_markup(reply_markup=main_keyboard)

        # Если текущее состояние - добавление описания нового кошелька
        elif current_state == FSMWallet.create_wallet_add_description:
            await state.set_state(FSMWallet.create_wallet_add_name)
            await callback.message.edit_text(LEXICON["create_new_name_wallet"],
                                             reply_markup=back_keyboard)

        ############################################################################################################
        # Если текущее состояние - добавление seed phrase для создания нового кошелька
        if current_state == FSMWallet.create_wallet_from_seed_add_seed:
            await state.set_state(default_state)
            await callback.message.edit_text(LEXICON["back_to_main_menu"])
            await callback.message.edit_reply_markup(reply_markup=main_keyboard)

        # Если текущее состояние - добавление имени нового кошелька
        elif current_state == FSMWallet.create_wallet_from_seed_add_name:
            await state.set_state(FSMWallet.create_wallet_from_seed_add_seed)
            await callback.message.edit_text(LEXICON["create_seed_wallet"], reply_markup=back_keyboard)

        # Если текущее состояние - добавление описания нового кошелька
        elif current_state == FSMWallet.create_wallet_from_seed_add_description:
            await state.set_state(FSMWallet.create_wallet_from_seed_add_name)
            await callback.message.edit_text(LEXICON["create_new_name_wallet"], reply_markup=back_keyboard)

        #############################################################################################################
        # Если текущее состояние - добавление адреса для подключения кошелька
        elif current_state == FSMWallet.connect_wallet_add_address:
            await state.set_state(default_state)
            await callback.message.edit_text(LEXICON["back_to_main_menu"])
            await callback.message.edit_reply_markup(reply_markup=main_keyboard)

        # Если текущее состояние - добавление имени для подключения кошелька
        elif current_state == FSMWallet.connect_wallet_add_name:
            await state.set_state(FSMWallet.connect_wallet_add_address)
            await callback.message.edit_text(LEXICON["connect_wallet_address"])
            await callback.message.edit_reply_markup(reply_markup=back_keyboard)

        # Если текущее состояние - добавление описания для подключения кошелька
        elif current_state == FSMWallet.connect_wallet_add_description:
            await state.set_state(FSMWallet.connect_wallet_add_name)
            await callback.message.edit_text(LEXICON["connect_wallet_add_name"], reply_markup=back_keyboard)
        #############################################################################################################
        # Если текущее состояние - выбор отправителя для трансфера
        elif current_state == FSMWallet.transfer_choose_sender_wallet:
            await state.set_state(default_state)
            await callback.message.edit_text(LEXICON["back_to_main_menu"])
            await callback.message.edit_reply_markup(reply_markup=main_keyboard)

        # Если текущее состояние - ввод приватного ключа отправителя для трансфера
        elif current_state == FSMWallet.transfer_sender_private_key:
            await state.set_state(FSMWallet.transfer_choose_sender_wallet)
            await callback.message.edit_text(LEXICON["list_sender_wallets"])
            # Получаем пользователя и его кошельки
            _, user_wallets = await retrieve_user_wallets(callback)
            wallet_keyboard = await get_wallet_keyboard(user_wallets)
            await callback.message.edit_reply_markup(reply_markup=wallet_keyboard)

        # Если текущее состояние - ввод адреса получателя для трансфера
        elif current_state == FSMWallet.transfer_recipient_address:
            await state.set_state(FSMWallet.transfer_sender_private_key)
            await callback.message.edit_text(LEXICON["transfer_sender_private_key_prompt"])
            await callback.message.edit_reply_markup(reply_markup=back_keyboard)

        # Если текущее состояние - ввод суммы для трансфера
        elif current_state == FSMWallet.transfer_amount:
            await state.set_state(FSMWallet.transfer_recipient_address)
            if CURRENT_BLOCKCHAIN == 'solana':
                await callback.message.edit_text(LEXICON["transfer_recipient_address_prompt"])
            elif CURRENT_BLOCKCHAIN == 'bsc':
                await callback.message.edit_text(LEXICON["transfer_recipient_address_prompt_bsc"])
            await callback.message.edit_reply_markup(reply_markup=back_keyboard)

        #############################################################################################################
        # Если текущее состояние - выбор кошелька для просмотра истории транзакций
        elif current_state == FSMWallet.choose_transaction_wallet:
            await state.set_state(default_state)
            await callback.message.edit_text(LEXICON["back_to_main_menu"])
            await callback.message.edit_reply_markup(reply_markup=main_keyboard)

        #############################################################################################################
        elif current_state == FSMWallet.delete_wallet:
            await state.set_state(default_state)
            await callback.message.edit_text(LEXICON["back_to_main_menu"])
            await callback.message.edit_reply_markup(reply_markup=main_keyboard)

        # Отправляем ответ на запрос обратного вызова для подтверждения обработки
        await callback.answer()
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_back_button: {e}\n{detailed_error_traceback}")
