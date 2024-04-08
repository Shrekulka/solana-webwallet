# solana_wallet_telegram_bot/database/database.py

import aiosqlite
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from config_data.config import config

# Получение параметров подключения к базе данных из конфигурационного файла
DB_ENGINE = config.db_engine                         # Тип используемого движка базы данных (SQLite или PostgreSQL)
DB_NAME = config.db_name                             # Название базы данных
DB_HOST = config.db_host                             # URL-адрес базы данных
DB_USER = config.db_user                             # Имя пользователя базы данных
DB_PASSWORD = config.db_password.get_secret_value()  # Пароль к базе данных (получаем его в зашифрованном виде)


# Если используется SQLite, создаем соответствующие объекты для работы с базой данных SQLite
if DB_ENGINE == 'sqlite':

    # Создание движка базы данных
    engine = create_async_engine(f"sqlite+aiosqlite:///{DB_NAME}.db", echo=True)

    # Создание сессии базы данных
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def get_db() -> AsyncSession:
        """
            Get a database session.

            Returns:
                AsyncSession: The database session.
        """
        # Открываем новую асинхронную сессию базы данных
        async with AsyncSessionLocal() as session:
            # Возвращаем сессию после завершения блока (сессия закроется автоматически)
            return session

    # Функция для создания базы данных
    async def create_database() -> None:
        """
            Create the database.

            Returns:
                None
        """
        # Устанавливаем соединение с базой данных SQLite и открываем асинхронный контекст сессии
        async with aiosqlite.connect(f"{DB_NAME}.db") as db:
            # Включаем поддержку внешних ключей для базы данных
            await db.execute("PRAGMA foreign_keys = ON")

            # Создаем таблицу пользователей (если не существует)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    telegram_id INTEGER,
                    username TEXT
                )
            """)

            # Создаем таблицу кошельков Solana (если не существует)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS solana_wallets (
                    id INTEGER PRIMARY KEY,
                    wallet_address TEXT,
                    balance REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    name TEXT,
                    description TEXT,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)

            # Применяем все изменения к базе данных
            await db.commit()


    async def init_database() -> None:
        """
            Initialize the database.

            Returns:
                None
        """
        # Открываем асинхронную сессию базы данных
        async with AsyncSessionLocal() as session:
            # Начинаем транзакцию в базе данных
            async with session.begin():
                # Вызываем функцию для создания базы данных
                await create_database()

# Если используется PostgreSQL, создаем соответствующие объекты для работы с базой данных PostgreSQL
elif DB_ENGINE == 'postgresql':

    # Создание движка базы данных
    engine = create_async_engine("postgresql+asyncpg://solanabot:solanabot@localhost:5432/solanabot")

    # Создание сессии базы данных
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def get_db() -> AsyncSession:
        """
           Get a database session.

           Returns:
               AsyncSession: The database session.
        """
        # Открываем новую асинхронную сессию базы данных
        async with AsyncSessionLocal() as session:
            # Возвращаем сессию после завершения блока (сессия закроется автоматически)
            return session

    from models.models import Base

    # Функция для инициализации базы данных
    async def init_database() -> None:
        """
            Initialize the database.

            Returns:
                None
        """
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # код для создания таблиц и других необходимых действий для инициализации базы данных
                # Создание всех таблиц в бд
                async with engine.begin() as conn:
                    # удалить все таблицы из бд
                    # await conn.run_sync(Base.metadata.drop_all)
                    # создать все таблицы в бд
                    await conn.run_sync(Base.metadata.create_all)
