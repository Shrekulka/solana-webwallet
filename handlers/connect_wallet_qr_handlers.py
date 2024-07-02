# solana_wallet_telegram_bot/handlers/connect_wallet_qr_handlers.py
import json
import traceback

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
########### django #########
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from keyboards.connect_wallet import connect_wallet_from_qr_keyboard
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
# from database.database import get_db
from logger_config import logger
from services.wallet_service import handle_wallet_address, handle_wallet_name, handle_wallet_description, \
    handle_wallet_name_input
from states.states import FSMWallet
from utils.qr_utils import parse_scanned_data

# from services.qr_scanner import scan_qr_code

# from sqlalchemy import select

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
connect_wallet_from_qr_router: Router = Router()


@connect_wallet_from_qr_router.callback_query(F.data == "callback_button_connect_wallet_from_qr",
                                              StateFilter(FSMWallet.connect_wallet_method_chosen))
async def process_connect_wallet_command(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.message.answer(LEXICON["connect_wallet_qr_scan_code"],
                                      reply_markup=connect_wallet_from_qr_keyboard)
        await state.set_state(FSMWallet.connect_wallet_qr_add_code)
        # Избегаем ощущения, что бот завис и избегаем исключение - если два раза подряд нажать на одну и ту же кнопку
        await callback.answer()
    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_connect_wallet_command: {error}\n{detailed_send_message_error}")
        # Возвращаем пользователя в состояние по умолчанию и выводим сообщение об ошибке
        await state.set_state(FSMWallet.default_state)
        await callback.answer(LEXICON["error_message"], reply_markup=main_keyboard)


@connect_wallet_from_qr_router.message(F.web_app_data, StateFilter(FSMWallet.connect_wallet_qr_add_code))
async def process_qr_scan_result(message: Message, state: FSMContext) -> None:
    try:
        scanned_data = json.loads(message.web_app_data.data)
        wallet_data = parse_scanned_data(scanned_data)

        # Обновляем данные состояния с полученными данными о кошельке
        await state.update_data(**wallet_data)

        # Обрабатываем адрес кошелька
        if await handle_wallet_address(message, state, wallet_data):
            logger.debug("handle_wallet_address")

            # # Обрабатываем имя кошелька
            # if await handle_wallet_name(message, state, wallet_data):
            handle_wallet_name_input(message, state, is_connect=False):
                logger.debug("handle_wallet_name")

                # Обрабатываем описание кошелька
                if await handle_wallet_description(message, state, wallet_data):
                    logger.debug("handle_wallet_description")

    except Exception as error:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_qr_scan_result: {error}\n{detailed_send_message_error}")