# solana_wallet_telegram_bot/handlers/other_handlers.py
import asyncio
import traceback

from aiogram import Router
from aiogram.types import Message

from lexicon.lexicon_en import LEXICON
from logger_config import logger

# Инициализируем роутер уровня модуля
other_router = Router()


@other_router.message()
async def process_unexpected_message(message: Message) -> None:
    """
        Responds to unknown messages by sending the text "unknown" to the user.

        Args:
            message (Message): Message object.

        Returns:
            None
    """
    # Выводим апдейт в терминал
    try:
        # Проверяем, может ли бот редактировать сообщения
        if message.chat.type == 'private':  # Проверяем, что чат является приватным
            if message.text:                # Проверяем, есть ли текст в сообщении
                sent_message = await message.answer(LEXICON["unexpected_message"], reply_markup=None)
                await asyncio.sleep(1)
                await message.delete()
                # Удаляем отправленное сообщение
                await sent_message.delete()
            else:
                logger.warning("Received message without text. Cannot edit.")
        else:
            logger.warning("Received message in a non-private chat. Cannot edit.")
    except Exception as error:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in process_unexpected_message handler: {error}\n{detailed_error_traceback}")
