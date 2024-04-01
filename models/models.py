# solana_wallet_telegram_bot/models/models.py
import traceback

from sqlalchemy import Column, Integer, String, Float, ForeignKey, select
from sqlalchemy import DateTime, func
from sqlalchemy.orm import relationship

from database.database import Base
from external_services.solana.solana import create_solana_wallet, is_valid_wallet_address, \
    get_wallet_address_from_private_key
from logger_config import logger


class SolanaWallet(Base):
    __tablename__ = 'solana_wallets'

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String, index=True, unique=True, nullable=False)
    private_key = Column(String, nullable=False)

    # Поля для хранения баланса кошелька
    balance = Column(Float, nullable=False, default=0.0)

    # Поля для хранения истории транзакций
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Поля для хранения дополнительной информации о кошельке
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)

    # Поля для хранения токенов, находящихся на кошельке
    token_balances = relationship('SolanaTokenBalance', back_populates='wallet')

    # Поля для хранения информации о пользователе, которому принадлежит кошелек
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='wallets')

    @classmethod
    async def wallet_create(cls, session, user_id, name, description=None):
        """
            Class method for creating a wallet.

            Args:
                session: Database session.
                user_id: User identifier.
                name: Wallet name.
                description (optional): Wallet description.

            Returns:
                SolanaWallet: The created wallet.
        """
        # Генерация нового кошелька Solana с помощью внешней функции create_solana_wallet()
        wallet_address, private_key = await create_solana_wallet()

        # Создание нового экземпляра класса SolanaWallet с указанными параметрами
        wallet = cls(wallet_address=wallet_address, private_key=private_key, user_id=user_id, name=name,
                     description=description)
        # Добавление созданного кошелька в сессию базы данных
        session.add(wallet)
        # Сохранение изменений в базе данных
        await session.commit()
        # Возвращение созданного кошелька
        return wallet

    @classmethod
    async def connect_wallet(cls, session, user_id, wallet_address: str, private_key: str) -> 'SolanaWallet':
        """
            Class method for connecting a wallet.

            Args:
                session: Database session.
                user_id: User identifier.
                wallet_address (str): Wallet address.
                private_key (str): Wallet private key.

            Returns:
                SolanaWallet: The connected wallet.

            Raises:
                ValueError: If the wallet address is invalid or does not match the private key.
        """
        # Проверка валидности адреса кошелька
        if not is_valid_wallet_address(wallet_address):
            raise ValueError("Неверный адрес кошелька")

        # Получение адреса кошелька из закрытого ключа
        derived_wallet_address = get_wallet_address_from_private_key(private_key)

        # Проверка соответствия адреса и закрытого ключа
        if derived_wallet_address != wallet_address:
            raise ValueError("Адрес кошелька не соответствует закрытому ключу")

        # Создание нового экземпляра класса SolanaWallet с переданными параметрами
        wallet = cls(wallet_address=wallet_address, private_key=private_key, user_id=user_id)
        # Добавление созданного кошелька в сессию базы данных
        session.add(wallet)
        # Сохранение изменений в базе данных
        await session.commit()

        # Возвращение созданного кошелька
        return wallet

    @classmethod
    async def update_wallet(cls, session, user_id, wallet_address, name=None, description=None):
        wallet = await cls.switch(session, user_id=user_id, wallet_address=wallet_address)
        if wallet:
            if name:
                wallet.name = name
            if description:
                wallet.description = description
            await session.commit()
        return wallet

    @classmethod
    async def delete(cls, session):
        session.delete(cls)
        await session.commit()

    @classmethod
    async def switch(cls, session, user_id, wallet_address):
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
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False, unique=True)
    username = Column(String, nullable=True)

    wallets = relationship('SolanaWallet', back_populates='user')


class SolanaTokenBalance(Base):
    __tablename__ = 'solana_token_balances'

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey('solana_wallets.id'), nullable=False)
    token_address = Column(String, nullable=False)
    balance = Column(Float, nullable=False, default=0.0)

    wallet = relationship('SolanaWallet', back_populates='token_balances')
