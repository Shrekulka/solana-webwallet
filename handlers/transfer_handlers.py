# solana_wallet_telegram_bot/handlers/transfer_handlers.py
import traceback

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from database.database import get_db
from external_services.solana.solana import is_valid_wallet_address, get_sol_balance, http_client, transfer_token
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from models.models import SolanaWallet
from states.states import FSMWallet

# Инициализируем роутер уровня модуля
transfer_router: Router = Router()


# Обработчик сообщения с состоянием FSMWallet.choose_sender_wallet
@transfer_router.message(StateFilter(FSMWallet.choose_sender_wallet))
async def process_choose_sender_wallet(message: Message, state: FSMContext) -> None:
    try:
        # Получение доступа к базе данных
        async with await get_db() as session:
            # Получение кошельков пользователя из базы данных
            user_wallets = await session.execute(select(SolanaWallet).filter_by(user_id=message.from_user.id))
            # Преобразование результатов запроса в список скаляров
            user_wallets = user_wallets.scalars().all()

        # Создание словаря для хранения опций кошельков
        wallet_options = {f"{wallet.name} ({wallet.wallet_address})": wallet for wallet in user_wallets}

        # Если текст сообщения есть в опциях кошельков
        if message.text in wallet_options:
            # Получение выбранного кошелька
            selected_wallet = wallet_options[message.text]
            # Обновление данных состояния с адресом и приватным ключом отправителя
            await state.update_data(sender_address=selected_wallet.wallet_address,
                                    sender_private_key=selected_wallet.private_key)
            # Отправка запроса на ввод адреса получателя
            await message.answer(LEXICON["transfer_recipient_address_prompt"])
            # Установка состояния ввода адреса получателя
            await state.set_state(FSMWallet.transfer_recipient_address)
        else:
            # Если выбран неверный кошелек, отправляем сообщение об ошибке
            await message.answer(LEXICON["invalid_wallet_choice"])
            # Запрос на повторный выбор отправителя
            await message.answer(LEXICON["choose_sender_wallet"])
    except Exception as e:
        # Обработка и логирование ошибки
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_choose_sender_wallet: {e}\n{detailed_error_traceback}")


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

        async with await get_db() as session:
            wallet = await SolanaWallet.switch(session, user_id=message.from_user.id, wallet_address=None)

        if wallet:
            balance = await get_sol_balance(wallet.wallet_address, http_client)

            if balance >= amount:
                data = await state.get_data()
                recipient_address = data.get("recipient_address")

                await transfer_token(wallet.wallet_address, wallet.private_key, recipient_address, amount, http_client)
                await message.answer(LEXICON["transfer_successful"].format(amount=amount, recipient=recipient_address))
            else:
                await message.answer(LEXICON["insufficient_balance"])
                await message.answer(LEXICON["transfer_amount_prompt"])
        else:
            await message.answer(LEXICON["no_wallet_connected"])

        await state.clear()
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_transfer_amount: {e}\n{detailed_error_traceback}")
