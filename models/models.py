# solana_wallet_telegram_bot/models/models.py


from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy import DateTime, func
from sqlalchemy.orm import relationship

from database.database import Base
from external_services.solana.solana import create_solana_wallet


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
    async def create(cls, session, user_id, name=None, description=None):
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

    async def delete(self, session):
        session.delete(self)
        await session.commit()

    @classmethod
    async def switch(cls, session, user_id, wallet_address):
        # Поиск кошелька в базе данных по указанному пользователю и адресу кошелька
        wallet = await session.query(cls).filter_by(user_id=user_id, wallet_address=wallet_address).first()
        # Если кошелек найден (не является None)
        if wallet:
            # Возвращаем найденный кошелек
            return wallet
        else:
            # Если кошелек не найден, возвращаем None
            # Добавляем обработку случая, когда кошелек не найден
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
