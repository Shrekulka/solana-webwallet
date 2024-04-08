# solana_wallet_telegram_bot/models/models.py

import traceback
from typing import Optional, Tuple

from sqlalchemy import Column, Integer, String, Float, ForeignKey, select
from sqlalchemy import DateTime, func
from sqlalchemy.orm import relationship, Session, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

from external_services.solana.solana import create_solana_wallet, is_valid_wallet_address
from logger_config import logger


class Base(AsyncAttrs, DeclarativeBase):
    """
        Base class for SQLAlchemy models.

        Attributes:
            AsyncAttrs (class): Asynchronous attribute access mixin.
            DeclarativeBase (class): Declarative base class for SQLAlchemy models.
    """
    pass


class SolanaWallet(Base):
    """
        Represents a Solana wallet entity.

        Attributes:
            id (int): The unique identifier for the wallet.
            wallet_address (str): The address of the wallet.
            balance (float): The balance of the wallet.
            created_at (DateTime): The datetime when the wallet was created.
            updated_at (DateTime): The datetime when the wallet was last updated.
            name (str, optional): The name of the wallet.
            description (str, optional): The description of the wallet.
            token_balances (relationship): Relationship to token balances associated with the wallet.
            user_id (int): The user identifier associated with the wallet.
            user (relationship): Relationship to the user owning the wallet.
    """
    # Определение имени таблицы в базе данных
    __tablename__ = 'solana_wallets'

    # Уникальный идентификатор кошелька
    id = Column(Integer, primary_key=True, index=True)

    # Адрес кошелька
    wallet_address = Column(String, index=True, unique=True, nullable=False)

    # Поля для хранения баланса кошелька
    balance = Column(Float, nullable=False, default=0.0)

    # Дата и время создания записи о кошельке
    created_at = Column(DateTime, server_default=func.now())

    # Дата и время последнего обновления записи о кошельке
    updated_at = Column(DateTime, onupdate=func.now())

    # Имя кошелька (необязательное поле)
    name = Column(String, nullable=True)

    # Описание кошелька (необязательное поле)
    description = Column(String, nullable=True)

    # Поля для хранения токенов, находящихся на кошельке
    token_balances = relationship('SolanaTokenBalance', back_populates='wallet')

    # Идентификатор пользователя, которому принадлежит кошелек
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Связь с таблицей пользователей
    user = relationship('User', back_populates='wallets')

    @classmethod
    async def wallet_create(cls, session: Session, user_id: int, name: Optional[str] = None,
                            description: Optional[str] = None) -> Tuple['SolanaWallet', str]:
        """
            Class method for creating a wallet.

            Args:
                session (Session): Database session.
                user_id (int): User identifier.
                name (str): Wallet name.
                description (str, optional): Wallet description.

            Returns:
                SolanaWallet: The created wallet.

            Raises:
                ValueError: If the wallet address is invalid or does not match the private key.
        """
        # Генерация нового кошелька Solana с помощью внешней функции create_solana_wallet()
        wallet_address, private_key = await create_solana_wallet()

        # Создание нового экземпляра класса SolanaWallet с указанными параметрами
        wallet = cls(wallet_address=wallet_address, user_id=user_id, name=name, description=description)
        # Добавление созданного кошелька в сессию базы данных
        session.add(wallet)
        # Сохранение изменений в базе данных
        await session.commit()
        # Возвращение кортежа из созданного кошелька и приватного ключа
        return wallet, private_key

    @classmethod
    async def connect_wallet(cls, session: Session, user_id: int, wallet_address: str, name: Optional[str] = None,
                             description: Optional[str] = None) -> 'SolanaWallet':
        """
            Class method for connecting a wallet.

            Args:
                session (Session): Database session.
                user_id (int): User identifier.
                wallet_address (str): Wallet address.
                name (str): Wallet name.
                description (str): Wallet description.

            Returns:
                SolanaWallet: The connected wallet.

            Raises:
                ValueError: If the wallet address is invalid or does not match the private key.
        """
        # Проверка валидности адреса кошелька
        if not is_valid_wallet_address(wallet_address):
            raise ValueError("Invalid wallet address")

        # Создание нового экземпляра класса SolanaWallet с переданными параметрами
        wallet = cls(wallet_address=wallet_address, user_id=user_id, name=name, description=description)
        # Добавление созданного кошелька в сессию базы данных
        session.add(wallet)
        # Сохранение изменений в базе данных
        await session.commit()

        # Возвращение созданного кошелька
        return wallet

    @classmethod
    async def update_wallet(cls, session: Session, user_id: int, wallet_address: str, name: Optional[str] = None,
                            description: Optional[str] = None) -> Optional['SolanaWallet']:
        """
            Class method for updating a wallet.

            Args:
                session (Session): Database session.
                user_id (int): User identifier.
                wallet_address (str): Wallet address.
                name (str, optional): New wallet name.
                description (str, optional): New wallet description.

            Returns:
                SolanaWallet: The updated wallet if successful, None otherwise.

            Raises:
                Exception: If an error occurs during the operation.
        """
        # Получение кошелька из базы данных по заданным параметрам
        wallet = await cls.switch(session, user_id=user_id, wallet_address=wallet_address)

        # Проверка наличия найденного кошелька
        if wallet:
            # Если указано новое имя, обновляем его в записи о кошельке
            if name:
                wallet.name = name
            # Если указано новое описание, обновляем его в записи о кошельке
            if description:
                wallet.description = description
            # Сохранение изменений в базе данных
            await session.commit()

        # Возвращение найденного или обновленного кошелька (или None, если кошелек не был найден)
        return wallet

    @classmethod
    async def delete(cls, session: Session) -> None:
        """
            Class method for deleting a wallet.

            Args:
                session (Session): Database session.

            Raises:
                Exception: If an error occurs during the operation.
        """
        # Удаление объекта класса из базы данных
        session.delete(cls)

        # Сохранение изменений в базе данных
        await session.commit()

    @classmethod
    async def switch(cls, session: Session, user_id: int, wallet_address: str) -> Optional['SolanaWallet']:
        """
            Class method for switching a wallet.

            Args:
                session (Session): Database session.
                user_id (int): User identifier.
                wallet_address (str): Wallet address.

            Returns:
                SolanaWallet: The switched wallet if found, None otherwise.

            Raises:
                Exception: If an error occurs during the operation.
        """
        try:
            # Выполняем запрос к базе данных
            result = await session.execute(select(cls).filter_by(user_id=user_id, wallet_address=wallet_address))
            # Получаем результаты запроса
            wallet = result.scalar_one_or_none()
            # Возвращаем найденный кошелек (или None, если не найден)
            return wallet
        except Exception as e:
            # Обработка ошибки
            detailed_error_traceback = traceback.format_exc()
            logger.error(f"Error during wallet switch: {e}\n{detailed_error_traceback}")
            return None


class User(Base):
    """
       Represents a user entity.

       Attributes:
           id (int): The unique identifier for the user.
           telegram_id (int): The Telegram identifier for the user.
           username (str, optional): The username of the user.
           wallets (relationship): Relationship to the user's wallets.
    """
    # Определение имени таблицы в базе данных
    __tablename__ = 'users'

    # Поле идентификатора пользователя с уникальным значением и первичным ключом
    id = Column(Integer, primary_key=True)

    # Поле идентификатора Telegram пользователя, не может быть пустым и должно быть уникальным
    telegram_id = Column(Integer, nullable=False, unique=True)

    # Поле имени пользователя, может быть пустым
    username = Column(String, nullable=True)

    # Отношение между таблицей пользователей и таблицей кошельков: каждый пользователь может иметь несколько кошельков
    wallets = relationship('SolanaWallet', back_populates='user')


class SolanaTokenBalance(Base):
    """
       Represents a Solana token balance entity.

       Attributes:
           id (int): The unique identifier for the token balance.
           wallet_id (int): The identifier of the wallet associated with the token balance.
           token_address (str): The address of the token.
           balance (float): The balance of the token.
           wallet (relationship): Relationship to the wallet associated with the token balance.
    """
    # Определение имени таблицы в базе данных
    __tablename__ = 'solana_token_balances'

    # Поле идентификатора с уникальным значением и первичным ключом
    id = Column(Integer, primary_key=True)

    # Поле идентификатора кошелька, к которому относится баланс токена, ссылается на таблицу solana_wallets
    wallet_id = Column(Integer, ForeignKey('solana_wallets.id'), nullable=False)

    # Поле адреса токена, не может быть пустым
    token_address = Column(String, nullable=False)

    # Поле баланса токена, не может быть пустым, имеет значение по умолчанию 0.0
    balance = Column(Float, nullable=False, default=0.0)

    # Отношение между таблицей балансов токенов и таблицей кошельков:
    # каждый баланс токена привязан к одному кошельку
    wallet = relationship('SolanaWallet', back_populates='token_balances')
