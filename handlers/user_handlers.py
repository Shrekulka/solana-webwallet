# solana_wallet_telegram_bot/handlers/user_handlers.py
import traceback

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.database import get_db
from external_services.solana.solana import (
    get_sol_balance, get_transaction_history, http_client, transfer_token, buy_token,
    sell_token)
from keyboards.main_keyboard import main_keyboard
from lexicon.lexicon_en import LEXICON
from logger_config import logger
from models.models import SolanaWallet, User
from states.states import FSMWallet

# Инициализируем роутер уровня модуля
user_router: Router = Router()


# Обработчик команды старта бота
@user_router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext) -> None:
    try:
        # Логирование информации о сообщении в формате JSON
        logger.info(message.model_dump_json(indent=4, exclude_none=True))

        # Отправка сообщения пользователю с приветственным текстом и клавиатурой
        start_message = await message.answer(
            LEXICON["/start"].format(first_name=message.from_user.first_name),
            reply_markup=main_keyboard)

        # Получение сессии базы данных
        async with await get_db() as session:
            # Поиск пользователя в базе данных по ID Telegram
            user = await session.execute(select(User).filter_by(telegram_id=message.from_user.id))
            user = user.scalar()
            # Если пользователь не найден, создаем новую запись о нем в базе данных
            if not user:
                new_user = User(telegram_id=message.from_user.id, username=message.from_user.username)
                session.add(new_user)
                await session.commit()
    except Exception as e:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_start_command: {e}\n{detailed_send_message_error}")


# Объявление функции обработки команды "/help"
@user_router.message(Command(commands='help'))
async def process_help_command(message: Message, state: FSMContext) -> None:
    try:
        # Выводим информацию об объекте сообщения в лог терминала
        logger.info(message.model_dump_json(indent=4, exclude_none=True))

        # Отправляем сообщение со справочной информацией о командах из лексикона
        await message.answer(LEXICON["/help"])
        # Отправляем дополнительное сообщение для продолжения с выбором пунктов меню
        await message.answer(LEXICON["start_message_continue"], reply_markup=main_keyboard)
    except Exception as e:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_create_wallet_command: {e}\n{detailed_send_message_error}")


@user_router.callback_query(F.data == "callback_button_create_wallet")
async def process_create_wallet_command(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        # Отправляем сообщение с просьбой ввести имя для кошелька
        await callback.message.edit_text(LEXICON["wallet_name_prompt"])
        # Переход в состояние добавления имени кошелька
        await state.set_state(FSMWallet.add_name_wallet)

    except Exception as e:
        detailed_send_message_error = traceback.format_exc()
        logger.error(f"Error in process_create_wallet_command: {e}\n{detailed_send_message_error}")


@user_router.callback_query(F.data == "callback_button_connect_wallet")
async def process_connect_wallet_command(callback: CallbackQuery, db: Session = get_db()) -> None:
    pass


@user_router.callback_query(F.data == "callback_button_balance")
async def process_balance_command(callback: CallbackQuery, db: Session = get_db()) -> None:
    """
        Handler for processing balance command callback.

        Args:
            callback (types.CallbackQuery): The callback query object.
            db (Session): SQLAlchemy session object.

        Returns:
            None
        """
    try:
        # Выполнение запроса к базе данных для получения кошелька пользователя по его идентификатору.
        result = db.execute(select(SolanaWallet).filter_by(user_id=callback.from_user.id))
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
    finally:
        db.close()


# изменить StateFilter
@user_router.callback_query(F.data == "callback_button_price", StateFilter(default_state))
async def process_get_token_price_command(callback: CallbackQuery, db: Session = get_db()) -> None:
    pass


# изменить StateFilter
@user_router.callback_query(F.data == "callback_button_buy", StateFilter(default_state))
async def process_buy_token_command(callback: CallbackQuery, db: Session = get_db()) -> None:
    """
       Handler for processing buy token command callback.

       Args:
           callback (types.CallbackQuery): The callback query object.
           db (Session): SQLAlchemy session object.

       Returns:
           None
       """
    try:
        # Выполнение запроса к базе данных для получения кошелька пользователя по его идентификатору.
        result = db.execute(select(SolanaWallet).filter_by(user_id=callback.from_user.id))
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
    finally:
        db.close()


# Объявление обработчика колбэка для кнопки "callback_button_sell".
@user_router.callback_query(F.data == "callback_button_sell")
async def process_sell_token_command(callback: CallbackQuery) -> None:
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
async def process_transfer_token_command(callback: CallbackQuery) -> None:
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
async def process_transactions_command(callback: CallbackQuery) -> None:
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
async def process_button_2_press(callback: CallbackQuery) -> None:
    pass
