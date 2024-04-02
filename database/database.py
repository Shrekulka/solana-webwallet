# solana_wallet_telegram_bot/database/database.py

import aiosqlite
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from config_data.config import config

DB_NAME = config.db_name
DB_HOST = config.db_host
DB_USER = config.db_user
DB_PASSWORD = config.db_password.get_secret_value()

# Создание движка базы данных
engine = create_async_engine(f"sqlite+aiosqlite:///{DB_NAME}.db", echo=True)

# Создание сессии базы данных
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        return session


# Функция для создания базы данных
async def create_database() -> None:
    async with aiosqlite.connect(f"{DB_NAME}.db") as db:
        await db.execute("PRAGMA foreign_keys = ON")
        # Create users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER,
                username TEXT
            )
        """)
        # Create solana_wallets table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS solana_wallets (
                id INTEGER PRIMARY KEY,
                wallet_address TEXT,
                private_key TEXT,
                balance REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                name TEXT,
                description TEXT,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        await db.commit()


# Функция для инициализации базы данных
async def init_database() -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await create_database()
            # код для создания таблиц и других необходимых действий для инициализации базы данных
