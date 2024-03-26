# solana_wallet_telegram_bot/handlers/user_handlers.py

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session  # Добавим импорт объекта сессии

from database.database import SessionLocal
from external_services.solana.solana import (
    get_sol_balance, get_transaction_history, http_client, transfer_token, buy_token,
    sell_token)
from keyboards.keyboards import wallet_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from models.models import SolanaWallet, User

# Инициализируем роутер уровня модуля
user_router: Router = Router()


@user_router.message(CommandStart())
async def process_start_command(message: Message, session: AsyncSession = SessionLocal()) -> None:
    """
        Handler for the "/start" command.

        Args:
            message (types.Message): The user's message object.
            session (Session): SQLAlchemy session object.

        Returns:
            None

        Sends a welcome message and adds the user to the database if they are not already present.
    """
    # Выводим апдейт в терминал
    logger.info(message.model_dump_json(indent=4, exclude_none=True))

    # Отправка приветственного сообщения, хранящегося в словаре LEXICON по ключу "/start".
    await message.answer(LEXICON[message.text].format(first_name=message.from_user.first_name),
                         reply_markup=wallet_keyboard)

    # Проверка наличия пользователя в базе данных
    user = await session.execute(select(User).filter_by(telegram_id=message.from_user.id))
    user = user.scalar()
    if not user:
        # Если пользователя нет в базе данных, добавляем его
        new_user = User(telegram_id=message.from_user.id, username=message.from_user.username)
        session.add(new_user)
        await session.commit()


# Этот хэндлер будет срабатывать на команду "/help"
# Будет отправлять пользователю сообщение со списком доступных команд в боте
@user_router.message(Command(commands='help'))
async def process_help_command(message: Message, session: AsyncSession = SessionLocal()) -> None:
    """
        Handler for the "/help" command.

        Args:
            message (types.Message): The user's message object.

        Returns:
            None

        Sends a message to the user with a list of available commands in the bot.
    """
    # Выводим апдейт в терминал
    logger.info(message.model_dump_json(indent=4, exclude_none=True))

    await message.answer(LEXICON[message.text])


# Обработчик для создания нового кошелька при нажатии на кнопку "Создать кошелек"
@user_router.callback_query(F.data == "callback_button_create_wallet")
async def process_create_wallet_command(callback: CallbackQuery, session: AsyncSession = SessionLocal()) -> None:
    # Создание нового объекта кошелька для текущего пользователя
    wallet = await SolanaWallet.create(session, callback.from_user.id)

    # Отправка ответа пользователю с уведомлением об успешном создании кошелька
    await callback.answer(LEXICON["create_wallet_success"].format(wallet_address=wallet.wallet_address))


@user_router.callback_query(F.data == "callback_button_connect_wallet")
async def process_connect_wallet_command(callback: CallbackQuery, session: AsyncSession = SessionLocal()) -> None:
    pass


# Объявление обработчика колбэка для кнопки "callback_button_balance".
@user_router.callback_query(F.data == "callback_button_balance")
async def process_balance_command(callback: CallbackQuery, session: AsyncSession = SessionLocal()) -> None:
    # Начало асинхронной транзакции с использованием сессии базы данных.
    async with session.begin():
        # Выполнение запроса к базе данных для получения кошелька пользователя по его идентификатору.
        result = await session.execute(select(SolanaWallet).filter_by(user_id=callback.from_user.id))
        # Извлечение первого результата запроса (кошелька пользователя).
        user_wallet = result.scalars().first()
        # Проверка наличия кошелька пользователя.
        if user_wallet:
            # Если кошелек пользователя существует, получаем его баланс.
            balance = await get_sol_balance(user_wallet.address, http_client)
            # Отправляем ответ пользователю с сообщением об успешном получении баланса.
            await callback.answer(LEXICON["balance_success"].format(balance=balance))
        else:
            # Если кошелек пользователя не найден, отправляем ответ с сообщением о том, что кошелек не зарегистрирован.
            await callback.answer(LEXICON["no_registered_wallet"])


@user_router.callback_query(F.data == "callback_button_price")
async def process_get_token_price_command(callback: CallbackQuery, session: AsyncSession = SessionLocal()) -> None:
    pass


# Объявление обработчика колбэка для кнопки "callback_button_buy".
@user_router.callback_query(F.data == "callback_button_buy")
async def process_buy_token_command(callback: CallbackQuery, session: AsyncSession = SessionLocal()) -> None:
    # Начало асинхронной транзакции с использованием сессии базы данных.
    async with session.begin():
        # Выполнение запроса к базе данных для получения кошелька пользователя по его идентификатору.
        result = await session.execute(select(SolanaWallet).filter_by(user_id=callback.from_user.id))
        # Извлечение первого результата запроса (кошелька пользователя).
        user_wallet = result.scalars().first()
        # Проверка наличия кошелька пользователя.
        if user_wallet:
            # Если кошелек пользователя существует, отправляем ответ с запросом на ввод информации о покупке.
            await callback.answer(LEXICON["input_prompt"])
            # Получаем данные о токене и сумме от пользователя.
            token_data = await callback.text()
            token_mint_address, amount = token_data.split()
            try:
                # Преобразование суммы в формат float.
                amount = float(amount)
                # Выполнение операции покупки токена.
                await buy_token(user_wallet, token_mint_address, amount, http_client)
                # Отправка ответа пользователю об успешной покупке токена.
                await callback.answer(LEXICON["buy_success"].format(amount=amount))
            except ValueError:
                # Обработка ошибки при некорректном формате ввода от пользователя.
                await callback.answer(LEXICON["send_invalid_format"])
        else:
            # Если кошелек пользователя не найден, отправляем ответ с сообщением о том, что кошелек не зарегистрирован.
            await callback.answer(LEXICON["no_registered_wallet"])


# Объявление обработчика колбэка для кнопки "callback_button_sell".
@user_router.callback_query(F.data == "callback_button_sell")
async def process_sell_token_command(callback: CallbackQuery, session: AsyncSession = SessionLocal()) -> None:
    # Начало асинхронной транзакции с использованием сессии базы данных.
    async with session.begin():
        # Выполнение запроса к базе данных для получения кошелька пользователя по его идентификатору.
        result = await session.execute(select(SolanaWallet).filter_by(user_id=callback.from_user.id))
        # Извлечение первого результата запроса (кошелька пользователя).
        user_wallet = result.scalars().first()
        # Проверка наличия кошелька пользователя.
        if user_wallet:
            # Если кошелек пользователя существует, отправляем ответ с запросом на ввод информации о продаже.
            await callback.answer(LEXICON["input_prompt"])
            # Получаем данные о токене и сумме от пользователя.
            token_data = await callback.text()
            token_mint_address, amount = token_data.split()
            try:
                # Преобразование суммы в формат float.
                amount = float(amount)
                # Выполнение операции продажи токена.
                await sell_token(user_wallet, token_mint_address, amount, http_client)
                # Отправка ответа пользователю об успешной продаже токена.
                await callback.answer(LEXICON["sell_success"].format(amount=amount))
            except ValueError:
                # Обработка ошибки при некорректном формате ввода от пользователя.
                await callback.answer(LEXICON["send_invalid_format"])
        else:
            # Если кошелек пользователя не найден, отправляем ответ с сообщением о том, что кошелек не зарегистрирован.
            await callback.answer(LEXICON["no_registered_wallet"])


# Объявление обработчика колбэка для кнопки "callback_button_transfer".
@user_router.callback_query(F.data == "callback_button_transfer")
async def process_transfer_token_command(callback: CallbackQuery, session: AsyncSession = SessionLocal()) -> None:
    # Начало асинхронной транзакции с использованием сессии базы данных.
    async with session.begin():
        # Выполнение запроса к базе данных для получения кошелька пользователя по его идентификатору.
        result = await session.execute(select(SolanaWallet).filter_by(user_id=callback.from_user.id))
        # Извлечение первого результата запроса (кошелька пользователя).
        user_wallet = result.scalars().first()
        # Проверка наличия кошелька пользователя.
        if user_wallet:
            # Если кошелек пользователя существует, отправляем ответ с запросом на ввод информации о трансфере токена.
            await callback.answer(LEXICON["input_prompt"])
            # Получаем данные о получателе, токене и сумме от пользователя.
            token_data = await callback.text()
            recipient_address, token_mint_address, amount = token_data.split()
            try:
                # Преобразование суммы в формат float.
                amount = float(amount)
                # Выполнение операции трансфера токена.
                await transfer_token(user_wallet, recipient_address, token_mint_address, amount, http_client)
                # Отправка ответа пользователю об успешном трансфере токена.
                await callback.answer(LEXICON["transfer_success"].format(recipient_address=recipient_address))
            except ValueError:
                # Обработка ошибки при некорректном формате ввода от пользователя.
                await callback.answer(LEXICON["send_invalid_format"])
        else:
            # Если кошелек пользователя не найден, отправляем ответ с сообщением о том, что кошелек не зарегистрирован.
            await callback.answer(LEXICON["no_registered_wallet"])


# Объявление обработчика колбэка для кнопки "callback_button_transaction".
@user_router.callback_query(F.data == "callback_button_transaction")
async def process_transactions_command(callback: CallbackQuery, session: AsyncSession = SessionLocal()) -> None:
    # Начало асинхронной транзакции с использованием сессии базы данных.
    async with session.begin():
        # Выполнение запроса к базе данных для получения кошелька пользователя по его идентификатору.
        result = await session.execute(select(SolanaWallet).filter_by(user_id=callback.from_user.id))
        # Извлечение первого результата запроса (кошелька пользователя).
        user_wallet = result.scalars().first()
        # Проверка наличия кошелька пользователя.
        if user_wallet:
            # Если кошелек пользователя существует, получаем историю транзакций для данного кошелька.
            transaction_history = await get_transaction_history(user_wallet.address, http_client)
            # Проверяем наличие истории транзакций.
            if transaction_history:
                # Если история транзакций существует, формируем сообщение с информацией о транзакциях.
                transaction_messages = [
                    # Форматирование каждого сообщения о транзакции с помощью LEXICON и данных из истории транзакций.
                    LEXICON["transaction_info"].format(
                        # Идентификатор транзакции, обрезанный до первых 8 символов для краткости.
                        transaction_id=transaction['transaction']['signatures'][0][:8],
                        # Отправитель транзакции - первый аккаунт в списке аккаунтов сообщения.
                        sender=transaction['transaction']['message']['accountKeys'][0],
                        # Получатель транзакции - второй аккаунт в списке аккаунтов сообщения.
                        recipient=transaction['transaction']['message']['accountKeys'][1],
                        # Разница в балансе отправителя до и после транзакции, выраженная в SOL.
                        amount=transaction['meta']['preBalances'][0] - transaction['meta']['postBalances'][0]
                    )
                    # Итерация по каждой транзакции в истории транзакций.
                    for transaction in transaction_history
                ]
                # Отправляем пользователю сообщение с информацией о транзакциях.
                await callback.answer("\n\n".join(transaction_messages))
            else:
                # Если история транзакций пуста, отправляем ответ с сообщением о пустой истории транзакций.
                await callback.answer(LEXICON["empty_history"])
        else:
            # Если кошелек пользователя не найден, отправляем ответ с сообщением о том, что кошелек не зарегистрирован.
            await callback.answer(LEXICON["no_registered_wallet"])


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery с data 'callback_button_delete_wallet'
@user_router.callback_query(F.data == "callback_button_delete_wallet")
async def process_button_2_press(callback: CallbackQuery, session: AsyncSession = SessionLocal()) -> None:
    pass

#
# @user_router.callback_query(F.data == "callback_button_send")
# async def process_send_sol_command(callback: CallbackQuery, session: AsyncSession = SessionLocal(),
# client=http_client) -> None:
#     user_wallet = session.query(SolanaWallet).filter_by(user_id=callback.from_user.id).first()
#     if user_wallet:
#         await callback.answer(LEXICON["send"])
#         await callback.answer(LEXICON["send_prompt"])
#         recipient_data = await callback.text()
#         recipient_address, amount = recipient_data.split()
#         try:
#             amount = float(amount)
#             await send_sol(user_wallet, recipient_address, amount, client)
#             await callback.answer(LEXICON["send_success"].format(amount=amount, recipient_address=recipient_address))
#         except ValueError:
#             await callback.answer(LEXICON["send_invalid_format"])
#     else:
#         await callback.answer(LEXICON["no_wallet"])
