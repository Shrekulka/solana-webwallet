# solana_wallet_telegram_bot/config_data/config.py

from typing import Union

from pydantic.v1 import BaseSettings, SecretStr


class Settings(BaseSettings):
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
