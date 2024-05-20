# solana_wallet_telegram_bot/handlers/main_menu_button_handler.py

import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery

from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger

# Инициализируем роутер уровня модуля
main_menu_button_router: Router = Router()


@main_menu_button_router.callback_query(F.data == "callback_button_return_main_keyboard", StateFilter(default_state))
async def process_return_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the press of the "Main Menu" button.

        Args:
            callback (CallbackQuery): The CallbackQuery object containing information about the call.
            state (FSMContext): The FSMContext object for working with chat states.

        Returns:
            None
    """
    try:
        # Отправляем сообщение с главным меню
        await callback.message.edit_text(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)
        # Избегаем ощущения, что бот завис и избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_return_main_menu: {error}\n{detailed_send_message_error}")