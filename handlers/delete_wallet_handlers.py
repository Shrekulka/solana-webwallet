# solana_wallet_telegram_bot/handlers/create_wallet_handlers.py

import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from states.states import FSMWallet

########### django #########
from django.contrib.auth import get_user_model
from applications.wallet.models import Wallet
from asgiref.sync import sync_to_async


@sync_to_async
def get_user(telegram_id):
    User = get_user_model()
    user = User.objects.filter(telegram_id=telegram_id).first()
    return user


@sync_to_async
def delete_wallet(user, wallet_address):
    wallet = Wallet.objects.filter(user=user, wallet_address=wallet_address).first()
    number_objects_deleted = wallet.delete()
    return number_objects_deleted

############################

# Инициализируем роутер уровня модуля
delete_wallet_router: Router = Router()


@delete_wallet_router.callback_query(F.data.startswith("wallet_address:"),
                                   StateFilter(FSMWallet.delete_wallet))
async def process_confirmation_delete_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the button press to confirmation a wallet deleting.

        Args:
            callback (CallbackQuery): The callback query object.
            state (FSMContext): The state context of the finite state machine.

        Returns:
            None
    """
    try:
        wallet_address = callback.data.split(":")[1]

        delete_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=LEXICON["button_delete_confirmation"], callback_data=f"del_wallet:{wallet_address}")],
                [InlineKeyboardButton(text=LEXICON["button_back"], callback_data="callback_button_back")],
            ]
        )

        await callback.message.answer(LEXICON["delete_wallet_confirmation"], reply_markup=delete_keyboard)

    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_wallet_name: {e}\n{detailed_error_traceback}")


@delete_wallet_router.callback_query(F.data.startswith("del_wallet:"), StateFilter(FSMWallet.delete_wallet))
async def process_delete_wallet_end(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the button press to confirmation a wallet deleting.

        Args:
            callback (CallbackQuery): The callback query object.
            state (FSMContext): The state context of the finite state machine.

        Returns:
            None
    """
    try:
        wallet_address = callback.data.split(":")[1]

        user = await get_user(telegram_id=callback.from_user.id)

        number_objects_deleted = await delete_wallet(user=user, wallet_address=wallet_address)

        if number_objects_deleted[0] == 1:
            await callback.message.answer(LEXICON["delete_wallet_successful"].format(wallet_address=wallet_address))
        else:
            await callback.message.answer(LEXICON["delete_wallet_not_successful"].format(wallet_address=wallet_address))

        await callback.message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)

        await state.clear()

    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_delete_wallet: {e}\n{detailed_error_traceback}")
