# solana_wallet_telegram_bot/handlers/wallet_handlers.py

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.database import get_db
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from models.models import SolanaWallet
from states.states import FSMWallet
from utils.validators import is_valid_wallet_name, is_valid_wallet_description

wallet_router: Router = Router()


@wallet_router.message(StateFilter(FSMWallet.add_name_wallet), lambda message: is_valid_wallet_name(message.text))
async def process_wallet_name(message: Message, state: FSMContext) -> None:
    """
    Handler for processing wallet name input.
    """
    try:
        logger.info(message.model_dump_json(indent=4, exclude_none=True))

        # Сохраняем введенное имя в хранилище по ключу "name"
        await state.update_data(wallet_name=message.text)
        data = await state.get_data()
        name = data.get("wallet_name")
        logger.info(f"Wallet name: {name}")
        await message.answer(text=LEXICON["wallet_name_confirmation"].format(wallet_name=name))
        await message.answer(text=LEXICON["wallet_name_confirmation_thanks"])
        await message.answer(text=LEXICON["wallet_description_prompt"])
        # Переходим к добавлению описания кошелька
        await state.set_state(FSMWallet.add_description_wallet)
    except Exception as e:
        logger.error(f"Error in process_wallet_name: {e}")


@wallet_router.message(StateFilter(FSMWallet.add_name_wallet))
async def process_invalid_wallet_name(message: Message, state: FSMContext) -> None:
    """
    Handler for processing invalid wallet name input.
    """
    try:
        await message.answer(text=LEXICON["invalid_wallet_name"])
        await message.answer(text=LEXICON["wallet_name_prompt"])
    except Exception as e:
        logger.error(f"Error in process_invalid_wallet_name: {e}")


@wallet_router.message(StateFilter(FSMWallet.add_description_wallet),
                       lambda message: is_valid_wallet_description(message.text))
async def process_wallet_description(message: Message, state: FSMContext) -> None:
    """
    Handler for processing wallet description input.
    """
    try:
        await state.update_data(description=message.text)
        data = await state.get_data()
        name = data.get("wallet_name")
        description = data.get("description")
        async with await get_db() as session:
            wallet = await SolanaWallet.create(session, message.from_user.id, name=name,
                                               description=description)
        await message.answer(
            LEXICON["wallet_created_successfully"].format(wallet_name=wallet.name,
                                                          wallet_description=wallet.description,
                                                          wallet_address=wallet.wallet_address,
                                                          private_key=wallet.private_key))
        # Завершаем состояние добавления кошелька
        await state.clear()
        await message.answer(LEXICON["continue_message"], reply_markup=main_keyboard)
    except Exception as e:
        logger.error(f"Error in process_wallet_description: {e}")


@wallet_router.message(StateFilter(FSMWallet.add_description_wallet))
async def process_invalid_wallet_description(message: Message, state: FSMContext) -> None:
    """
    Handler for processing invalid wallet description input.
    """
    try:
        await message.answer(text=LEXICON["invalid_wallet_description"])
        await message.answer(text=LEXICON["wallet_description_prompt"])
    except Exception as e:
        logger.error(f"Error in process_invalid_wallet_description: {e}")
