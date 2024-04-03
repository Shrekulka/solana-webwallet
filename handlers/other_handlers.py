# solana_wallet_telegram_bot/handlers/other_handlers.py
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
    logger.info(message.model_dump_json(indent=4, exclude_none=True))
    try:
        # Отправляем сообщение обратно пользователю с текстом "unknown"
        await message.reply(text=LEXICON["unexpected_message"])
    except Exception as error:
        # В случае возникновения ошибки выводим ее в лог
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Error in answer_to_unknown handler: {error}\n{detailed_error_traceback}")
