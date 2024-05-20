# solana_wallet_telegram_bot/config_data/config.py

from typing import Union
from httpx import Timeout
from pydantic.v1 import BaseSettings, SecretStr

# Константа для определения URL-адреса узла Solana в тестовой сети Devnet
SOLANA_NODE_URL = "https://api.testnet.solana.com"
# SOLANA_NODE_URL = "https://api.devnet.solana.com"

# Например, установить таймаут на чтение ответа 120 секунд, таймаут на соединение 20 секунд
timeout_settings = Timeout(read=120.0, connect=20.0, write=None, pool=None)

# Константа для определения соотношения между лампортами и SOL. 1 SOL = 10^9 лампортов.
LAMPORT_TO_SOL_RATIO = 10 ** 9

# Константа для определения длины шестнадцатеричного представления приватного ключа в символах.
PRIVATE_KEY_HEX_LENGTH = 64

# Константа для определения длины двоичного представления приватного ключа в байтах.
PRIVATE_KEY_BINARY_LENGTH = 32

# Константа, определяющая длительность существования кеша для истории транзакций (в секундах).
# Здесь установлено значение 3600 секунд (1 час).
TRANSACTION_HISTORY_CACHE_DURATION = 3600

# Константа для определения максимального количества транзакций в истории
TRANSACTION_LIMIT = 5


class Settings(BaseSettings):
    """
        Settings class for configuring the application.

        Attributes:
            db_engine (str): Database engine.
            db_name (str): Name of the database.
            db_host (str): URL address of the database.
            db_user (str): Username for the database.
            db_password (SecretStr): Password for the database.
            bot_token (SecretStr): Token for the bot.
            admin_ids (Union[list[int], int]): List of bot administrators' IDs.
    """
    db_engine: str                    # движок бд
    db_name: str                      # Название базы данных
    db_host: str                      # URL-адрес базы данных
    db_user: str                      # Имя пользователя базы данных
    db_password: SecretStr            # Пароль к базе данных
    bot_token: SecretStr              # Токена бота
    admin_ids: Union[list[int], int]  # Список id администраторов бота

    class Config:
        """
            Settings for working with Pydantic.

            This nested class defines parameters for loading environment variables from the `.env` file.

            Attributes:
                env_file (str): The name of the file containing environment variables.
                env_file_encoding (str): The encoding of the file containing environment variables.
        """
        # Указание файла .env для загрузки переменных окружения
        env_file = ".env"
        # Указание кодировки файла .env
        env_file_encoding = "utf-8"


# Создание экземпляра класса Settings для хранения конфигурационных данных
config: Settings = Settings()
