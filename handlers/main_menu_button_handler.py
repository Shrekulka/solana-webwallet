# solana_wallet_telegram_bot/handlers/main_menu_button_handler.py

import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from states.states import FSMWallet

# Инициализируем роутер уровня модуля
main_menu_button_router: Router = Router()


@main_menu_button_router.callback_query(F.data == "callback_button_return_main_keyboard", StateFilter(FSMWallet))
async def process_return_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    logger.info("You are in def process_return_main_menu!!!")
    try:
        current_state = await state.get_state()
        logger.info(f"State set to: {current_state}")
        if current_state in [
            FSMWallet.create_wallet_add_name,
            FSMWallet.connect_wallet_add_address,
            FSMWallet.transfer_choose_sender_wallet,
            FSMWallet.choose_transaction_wallet,
            FSMWallet.crypto_price_input,
        ]:
            await state.clear()  # или await state.set_state(default_state)
            await callback.message.edit_text(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)
        elif current_state == FSMWallet.create_wallet_add_description:
            await state.clear()  # или await state.set_state(default_state)
            await callback.message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)
        # Избегаем ощущения - бот завис и избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_return_main_menu: {error}\n{detailed_send_message_error}")
