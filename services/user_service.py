# solana_wallet_telegram_bot/services/user_service.py
from typing import Tuple, Optional

from aiogram.types import User
from asgiref.sync import sync_to_async
########### django #########
from django.contrib.auth import get_user_model


# from database.database import get_db


# from sqlalchemy import select


#
# @sync_to_async
# def get_user(telegram_id):
#     # DjangoUser = get_user_model()
#     user = User.objects.filter(telegram_id=telegram_id).first()
#     return user
#
# ############################


@sync_to_async
def update_or_create_user(telegram_id: int, defaults: dict) -> Tuple[User, bool]:
    """
        Asynchronously updates or creates a user based on their Telegram identifier.

        Args:
            telegram_id (int): The Telegram identifier of the user.
            defaults (dict): A dictionary containing data to update or create the user with.

        Returns:
            Tuple[User, bool]: A tuple consisting of the user object and a flag indicating if a new user was created.

        Raises:
            None
    """
    # Получаем модель пользователя
    user_model = get_user_model()
    # Обновляем или создаем пользователя по его идентификатору Telegram
    user, created = user_model.objects.update_or_create(telegram_id=telegram_id, defaults=defaults)
    # Возвращаем объект пользователя и флаг, указывающий на создание
    return user, created


@sync_to_async
def get_user(telegram_id: int) -> Optional[User]:
    """
        Asynchronously retrieves a user based on their Telegram identifier.

        Args:
            telegram_id (int): The Telegram identifier of the user.

        Returns:
            Optional[User]: The user object if it exists, otherwise None.

        Raises:
            None
    """
    # Получаем модель пользователя
    user_model = get_user_model()
    # Получаем пользователя по его идентификатору Telegram
    user = user_model.objects.filter(telegram_id=telegram_id).first()
    # Возвращаем объект пользователя
    return user
