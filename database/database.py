# solana_wallet_telegram_bot/database/database.py

import aiosqlite
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from config_data.config import config
from logger_config import logger

# Получение параметров подключения к базе данных из переменных окружения
DB_NAME = config.db_name
DB_HOST = config.db_host
DB_USER = config.db_user
DB_PASSWORD = config.db_password.get_secret_value()

try:
    # Строка подключения к базе данных SQLite
    SQLITE_DB_PATH = f"{DB_NAME}.db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"

    # Создание асинхронного соединения с базой данных
    async with aiosqlite.connect(SQLITE_DB_PATH) as async_conn:
        async with async_conn.cursor() as cursor:
            # Создание базового класса для моделей, определенных в базе данных
            Base = sqlalchemy.orm.declarative_base()

            # Создание асинхронной сессии для взаимодействия с базой данных
            AsyncSessionLocal = sessionmaker(
                bind=async_conn,
                expire_on_commit=False,
                class_=AsyncSession,
                autocommit=True,
                autoflush=True
            )

            # Определение моделей и создание соответствующих таблиц в базе данных
            from models import models

            # Создание таблиц в базе данных
            Base.metadata.create_all(async_conn)

except (sqlalchemy.exc.SQLAlchemyError, FileNotFoundError) as e:
    logger.error(f"Database error occurred: {str(e)}")
    # Выбрасываем исключение в случае ошибки базы данных
    raise RuntimeError("Database error occurred")
