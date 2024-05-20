# solana_wallet_telegram_bot/handlers/transaction_handlers.py

import json
import asyncio
import traceback
from decimal import Decimal

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery

from external_services.solana.solana import get_transaction_history
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from services.wallet_service import format_transaction_message, format_transaction_from_db_message
from states.states import FSMWallet
from config_data.config import SOLANA_NODE_URL, LAMPORT_TO_SOL_RATIO

########### django #########
from applications.wallet.models import Wallet, Transaction
from asgiref.sync import sync_to_async


@sync_to_async
def get_transaction_history_from_db(wallet_address):
    transaction_history_from_db = []
    wallet = Wallet.objects.filter(wallet_address=wallet_address).first()
    if wallet:
        transaction_history_from_db = wallet.transactions.all().order_by('-transaction_time')
    return transaction_history_from_db


@sync_to_async
def save_transaction(tr):
    address_list = []
    wallets = None
    tr_dict =  json.loads(tr.to_json())

    transaction_id = tr_dict['transaction']['signatures'][0] or ''
    sender = tr_dict['transaction']['message']['accountKeys'][0] or ''
    recipient = tr_dict['transaction']['message']['accountKeys'][1] or ''
    slot = tr_dict['slot'] or None
    transaction_time = tr_dict['blockTime'] or None
    transaction_status = f"{tr_dict['meta']['status'] or ''}"
    transaction_err = f"{tr_dict['meta']['err']  or ''}"
    pre_balances = tr_dict['meta']['preBalances'][0] or None
    post_balances = tr_dict['meta']['postBalances'][0] or None

    if sender:
        address_list.append(sender)

    if recipient:
        address_list.append(recipient)

    if address_list:
        wallets = Wallet.objects.filter(wallet_address__in=address_list)

    if wallets and transaction_id:
        transaction_obj = Transaction.objects.filter(transaction_id=transaction_id).first()

        if transaction_obj:
            # if the transaction exists - update the wallets
            transaction_obj.wallet.set(wallets)

        else:
            try:
                create_transaction_obj = Transaction.objects.create(
                    transaction_id =transaction_id,
                    slot=slot,
                    transaction_time=transaction_time,
                    sender=sender,
                    recipient=recipient,
                    pre_balances=pre_balances,
                    post_balances=post_balances,
                    transaction_status=transaction_status,
                    transaction_err=transaction_err,
                )
                create_transaction_obj.wallet.set(wallets)
            except Exception as er:
                print(f'Error create transaction: {er}')

    return None

############################


# Инициализируем роутер уровня модуля
transaction_router: Router = Router()


@transaction_router.callback_query(F.data.startswith("wallet_address:"),
                                   StateFilter(FSMWallet.choose_transaction_wallet))
async def process_choose_transaction_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    """
        Handles the button press to select a wallet address for fetching transaction history.

        Args:
            callback (CallbackQuery): The callback query object.
            state (FSMContext): The state context of the finite state machine.

        Returns:
            None
    """
    try:
        transaction_history = []
        tr_from_db_tasks = []
        transaction_id_before = None
        transaction_limit = 5
        transaction_max_limit = 100

        # Извлекаем адрес кошелька из callback_data
        wallet_address = callback.data.split(":")[1]

        tr_history_from_db = await get_transaction_history_from_db(wallet_address)
        tr_from_db_time_list = [tr.transaction_time async for tr in tr_history_from_db]

        if not tr_from_db_time_list:
            # если в бд нет трансакций то запросим из блокчейна 100 последних
            transaction_limit = transaction_max_limit

        while transaction_max_limit > 0:
            transaction_max_limit -= transaction_limit

            # api.devnet.solana.com выдает ошибку при попытке получить историю трансакций
            if "api.devnet.solana.com" not in SOLANA_NODE_URL:
                # Получаем историю транзакций кошелька по его адресу.
                transaction_history += await get_transaction_history(wallet_address, transaction_id_before, transaction_limit)

            if transaction_history:

                if transaction_history[-1].block_time in tr_from_db_time_list:
                    el_index = tr_from_db_time_list.index(transaction_history[-1].block_time)
                    if (el_index + 1) < len(tr_history_from_db):
                        tr_from_db_tasks = [format_transaction_from_db_message(tr) for tr in tr_history_from_db[el_index + 1:]]
                    break

                else:
                    transaction_id_before = transaction_history[-1].transaction.transaction.signatures[0]

        if transaction_history:
            for tr in transaction_history:
                await save_transaction(tr)

        if transaction_history or tr_from_db_tasks:

            # Создаем список задач на форматирование сообщений о транзакциях
            transaction_tasks = [format_transaction_message(transaction) for transaction in transaction_history]

            # if tr_from_db_tasks:
            transaction_tasks += tr_from_db_tasks

            # Используем asyncio.gather для параллельной обработки транзакций
            transaction_messages = await asyncio.gather(*transaction_tasks)

            # Объединяем все сообщения в одну строку с разделителем '\n\n'
            combined_message = '\n\n'.join(transaction_messages)

            # Отправляем объединенное сообщение
            await callback.message.answer(combined_message)
        else:
            # Отправляем ответ пользователю с сообщением о пустой истории транзакций
            await callback.answer(LEXICON["empty_history"], show_alert=True, reply_markup=None)

        # Очищаем состояние перед завершением
        await state.clear()

        # Отправляем сообщение с инструкцией о продолжении и клавиатурой основных кнопок
        await callback.message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)

        # Отвечаем на callback запрос, чтобы избежать ощущения зависания и исключений
        # await callback.answer()
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in choose_transaction_wallet: {e}\n{detailed_error_traceback}")
        # Отправляем сообщение пользователю о недоступности сервера и просьбе повторить запрос позже
        await callback.answer(LEXICON["server_unavailable"], show_alert=True, reply_markup=None)
        # Возвращаем пользователя в главное меню
        # await callback.message.delete()
        await callback.message.answer(LEXICON["back_to_main_menu"], reply_markup=main_keyboard)
        await state.set_state(default_state)

        await callback.answer()
