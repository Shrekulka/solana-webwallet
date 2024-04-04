# solana_wallet_telegram_bot/bot.py

import asyncio
import traceback

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis

from config_data.config import config
from database.database import init_database
from handlers import (
    user_handlers,
    create_wallet_handlers,
    connect_wallet_handlers,
    transfer_handlers,
    transaction_handlers, other_handlers, back_button_handler,
)
from logger_config import logger


# Функция конфигурирования и запуска бота
async def main() -> None:
    """
        Function to configure and run the bot.

        Initializes the bot and dispatcher, registers routers, skips accumulated updates,
        and starts polling.

        Returns:
            None
    """
    # # Инициализируем Redis
    # redis = Redis(host='localhost')
    #
    # # Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
    # storage = RedisStorage(redis=redis)

    logger.info("Initializing bot...")
    # Инициализируем бот и диспетчер
    bot: Bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode='HTML'))
    dp: Dispatcher = Dispatcher()#(storage=storage)
    logger.info("Bot initialized successfully.")

    # Сохраняем объект bot в хранилище workflow_data диспетчера dp. Это позволит использовать один и тот же объект
    # bot во всех обработчиках без необходимости явно передавать его из функции в функцию
    # dp.workflow_data['bot'] = bot

    # Регистрируем роутеры в диспетчере
    dp.include_router(user_handlers.user_router)
    dp.include_router(create_wallet_handlers.create_wallet_router)
    dp.include_router(connect_wallet_handlers.connect_wallet_router)
    dp.include_router(transfer_handlers.transfer_router)
    dp.include_router(transaction_handlers.transaction_router)
    dp.include_router(other_handlers.other_router)
    dp.include_router(back_button_handler.back_button_router)
    # Проверяем наличие базы данных и инициализируем ее при необходимости
    await init_database()

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    # Обработка прерывания пользователем
    except KeyboardInterrupt:
        logger.warning("Application terminated by the user")
    # Обработка неожиданных ошибок
    except Exception as error:
        # Получение подробной информации об ошибке
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Unexpected error in the application: {error}\n{detailed_send_message_error}")
