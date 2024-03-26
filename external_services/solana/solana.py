# solana_wallet_telegram_bot/external_services/solana/solana.py
import traceback
from typing import Tuple

import requests
from solana.rpc.api import Client, Keypair
from solana.transaction import Transaction
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address, create_associated_token_account, transfer_checked, \
    TransferCheckedParams

from logger_config import logger

# Создание клиента для подключения к тестовой сети Devnet
http_client = Client("https://api.devnet.solana.com")


async def create_solana_wallet() -> Tuple[str, str]:
    """
        Generate a new Solana wallet.

        Returns:
            Tuple[str, str]: A tuple containing the public address and private key of the generated wallet.

        Raises:
            Exception: If there's an error during the wallet creation process.
    """
    try:
        # Генерация нового кошелька
        keypair = Keypair()
        # Получение публичного адреса кошелька
        wallet_address = str(keypair.pubkey())
        # Получение приватного ключа кошелька и преобразование в шестнадцатеричное представление
        private_key = keypair.secret().hex()

        # Возвращаем публичный адрес кошелька и приватный ключ кошелька как кортеж
        return wallet_address, private_key

    # Если происходит ошибка с ключом (KeyError) или значением (ValueError)
    except (KeyError, ValueError) as e:
        detailed_error_traceback = traceback.format_exc()
        # Логирование ошибки
        logger.error(f"Failed to create Solana wallet: {e}\n{detailed_error_traceback}")
        # Поднятие нового исключения с подробной информацией
        raise Exception(f"Failed to create Solana wallet: {e}\n{detailed_error_traceback}")


async def get_sol_balance(wallet_address, client):
    try:
        # Получение баланса кошелька
        balance = await client.get_balance(Pubkey(wallet_address))

        # Преобразование лампортов в SOL
        sol_balance = balance / 10 ** 9

        # Возвращаем баланс кошелька в SOL после преобразования лампортов
        return sol_balance

    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        # Логирование ошибки
        logger.error(f"Failed to get Solana balance: {e}\n{detailed_error_traceback}")
        # Дополнительная обработка ошибки, если необходимо
        raise Exception(f"Failed to get Solana balance: {e}\n{detailed_error_traceback}")


async def get_token_price(token_mint_address):
    # Формирование URL для запроса цены токена к внешнему API - надо доработать
    api_url = f"https://api.example.com/token-prices/{token_mint_address}"
    try:
        # Отправка GET запроса к API для получения информации о цене токена
        response = requests.get(api_url)
        # Проверка на наличие ошибок HTTP
        response.raise_for_status()
        # Преобразование ответа в формат JSON
        token_data = response.json()
        # Извлечение цены токена из полученных данных
        token_price = token_data["price"]

        # Возвращение цены токена
        return token_price

    # Обработка ошибок запроса (например, проблемы с сетью)
    except requests.RequestException as e:
        logger.error(f"Failed to fetch token price: {e}")
        detailed_error_traceback = traceback.format_exc()
        raise Exception(f"Failed to fetch token price: {e}\n{detailed_error_traceback}")
    # Обработка неправильного формата ответа от API (отсутствует ключ 'price')
    except KeyError:
        logger.error("Invalid response format: missing 'price' key")
        detailed_error_traceback = traceback.format_exc()
        raise Exception(f"Invalid response format: missing 'price' key\n{detailed_error_traceback}")


async def buy_token(wallet, token_mint_address, amount, client):
    try:
        # Получение ассоциированного токенового аккаунта для указанного кошелька
        associated_token_account = get_associated_token_address(wallet.public_key(), token_mint_address)

        # Получение информации о токеновом аккаунте
        account_info = await client.get_account_info(associated_token_account)
        # Если ассоциированный токеновый аккаунт не существует
        if account_info is None:
            # Создание объекта транзакции для выполнения операции покупки токенов
            transaction = Transaction()
            # Создание инструкции для создания ассоциированного токенового аккаунта
            create_account_instruction = create_associated_token_account(
                # Оплата комиссии за создание аккаунта происходит с кошелька отправителя
                payer=wallet.public_key(),
                # Владелец создаваемого аккаунта - также кошелек отправителя
                owner=wallet.public_key(),
                # Адрес монетного токена, для которого создается ассоциированный аккаунт
                mint=token_mint_address, )

            # Добавление инструкции создания ассоциированного токенового аккаунта к транзакции.
            transaction.add(create_account_instruction)
            # Подписание транзакции с использованием приватного ключа кошелька.
            transaction.sign(wallet)
            # Отправка подписанной транзакции в блокчейн.
            await client.send_transaction(transaction)

        # Получение информации о цене токена с внешнего API
        token_price = await get_token_price(token_mint_address)

        # Вычисление количества токенов, которое можно купить на указанную сумму SOL
        sol_amount = amount / token_price
        # Преобразование в мелкие единицы
        token_amount = int(sol_amount * 10 ** 9)

        # Параметры для выполнения транзакции покупки токенов.
        transfer_params = TransferCheckedParams(
            # Количество токенов для покупки, выраженное в мелких единицах.
            amount=token_amount,
            # Количество десятичных знаков токена.
            decimals=6,
            # Адрес целевого токенового аккаунта, куда будут отправлены купленные токены.
            dest=associated_token_account,
            # Адрес монетного токена.
            mint=token_mint_address,
            # Публичный ключ владельца кошелька, который покупает токены.
            owner=wallet.public_key(),
            # Идентификатор программы для работы с токенами.
            program_id=TOKEN_PROGRAM_ID,
            # Источник токенов, который указывается как публичный ключ кошелька.
            source=wallet.public_key(), )
        # Создание инструкции для выполнения проверенной транзакции покупки токенов.
        transfer_instruction = transfer_checked(transfer_params)

        # Создание новой транзакции.
        transaction = Transaction()
        # Добавление инструкции перевода токенов в созданную транзакцию.
        transaction.add(transfer_instruction)
        # Подписание транзакции с использованием приватного ключа кошелька отправителя.
        transaction.sign(wallet)
        # Отправка подписанной транзакции в сеть блокчейна.
        await client.send_transaction(transaction)

    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        # Логирование ошибки
        logger.error(f"Failed to buy token: {e}\n{detailed_error_traceback}")
        # Дополнительная обработка ошибки, если необходимо
        raise Exception(f"Failed to buy token: {e}\n{detailed_error_traceback}")


async def sell_token(wallet, token_mint_address, amount, client):
    try:
        # Получение ассоциированного токенового аккаунта для указанного кошелька и мята
        associated_token_account = get_associated_token_address(wallet.public_key(), token_mint_address)

        # Получение информации о цене токена с внешнего API
        token_price = await get_token_price(token_mint_address)

        # Вычисление суммы SOL, которую можно получить за указанное количество токенов
        sol_amount = amount * token_price

        # Параметры для выполнения проверенной транзакции продажи токенов.
        transfer_params = TransferCheckedParams(
            # Количество токенов для продажи, выраженное в мелких единицах.
            amount=int(amount * 10 ** 9),
            # Количество десятичных знаков токена.
            decimals=6,
            # Публичный ключ кошелька, на который будут отправлены вырученные средства от продажи токенов.
            dest=wallet.public_key(),
            # Адрес монетного токена.
            mint=token_mint_address,
            # Публичный ключ владельца токенов, который продает токены.
            owner=associated_token_account,
            # Идентификатор программы для работы с токенами.
            program_id=TOKEN_PROGRAM_ID,
            # Источник токенов, который указывается как публичный ключ ассоциированного токенового аккаунта.
            source=associated_token_account,
        )

        # Создание инструкции для выполнения проверенной транзакции продажи токенов.
        transfer_instruction = transfer_checked(transfer_params)

        # Создание новой транзакции.
        transaction = Transaction()
        # Добавление инструкции перевода токенов в созданную транзакцию.
        transaction.add(transfer_instruction)
        # Подписание транзакции с использованием приватного ключа кошелька отправителя.
        transaction.sign(wallet)
        # Отправка подписанной транзакции в сеть блокчейна.
        await client.send_transaction(transaction)

        # Создание параметров для перевода SOL.
        transfer_params = TransferParams(
            # Публичный ключ отправителя SOL.
            from_pubkey=wallet.public_key(),
            # Публичный ключ получателя SOL, который является таким же, как и отправитель, так как SOL переводится на
            # тот же кошелек.
            to_pubkey=wallet.public_key(),
            # Количество лампортов для перевода, преобразованное из суммы SOL.
            lamports=int(sol_amount * 10 ** 9),
        )
        # Создание инструкции перевода SOL с использованием параметров перевода.
        transfer_instruction = transfer(transfer_params)

        # Создание новой транзакции.
        transaction = Transaction()
        # Добавление инструкции перевода SOL в созданную транзакцию.
        transaction.add(transfer_instruction)
        # Отправка транзакции в блокчейн через клиент.
        await client.send_transaction(transaction)

    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        # Логирование ошибки
        logger.error(f"Failed to sell token: {e}\n{detailed_error_traceback}")
        # Дополнительная обработка ошибки, если необходимо
        raise Exception(f"Failed to sell token: {e}\n{detailed_error_traceback}")


async def transfer_token(sender_wallet, recipient_address, token_mint_address, amount, client):
    try:
        # Получение ассоциированного токенового аккаунта отправителя
        sender_associated_token_account = get_associated_token_address(sender_wallet.public_key(), token_mint_address)

        # Получение ассоциированного токенового аккаунта получателя
        recipient_associated_token_account = get_associated_token_address(recipient_address, token_mint_address)

        # Получение информации о токеновом аккаунте получателя
        account_info = await client.get_account_info(recipient_associated_token_account)

        # Если токеновый аккаунт получателя не существует
        if account_info is None:
            # Создание объекта транзакции
            transaction = Transaction()
            # Создание инструкции для создания ассоциированного токенового аккаунта получателя
            create_account_instruction = create_associated_token_account(
                payer=sender_wallet.public_key(),  # Оплата комиссии за создание аккаунта с кошелька отправителя
                owner=Pubkey(recipient_address),  # Владелец нового токенового аккаунта
                mint=token_mint_address, )  # Монетный мят токена

            # Добавление инструкции создания токенового аккаунта в транзакцию
            transaction.add(create_account_instruction)
            # Подписание транзакции с помощью приватного ключа отправителя
            transaction.sign(sender_wallet)
            # Отправка транзакции в блокчейн
            await client.send_transaction(transaction)

        # Определение параметров для проверенного перевода токенов
        transfer_params = TransferCheckedParams(
            # Количество переводимых токенов в мелких единицах
            amount=int(amount * 10 ** 9),
            # Количество десятичных знаков токена
            decimals=6,
            # Адрес назначения - ассоциированный токеновый аккаунт получателя
            dest=recipient_associated_token_account,
            # Адрес монетного токена
            mint=token_mint_address,
            # Публичный ключ отправителя - владельца токенов
            owner=sender_associated_token_account,
            # Идентификатор программы для работы с токенами
            program_id=TOKEN_PROGRAM_ID,
            # Источник токенов - ассоциированный токеновый аккаунт отправителя
            source=sender_associated_token_account, )

        # Создание инструкции проверенного перевода токенов
        transfer_instruction = transfer_checked(transfer_params)

        # Создание новой транзакции
        transaction = Transaction()
        # Добавление инструкции перевода токенов к транзакции
        transaction.add(transfer_instruction)
        # Подписание транзакции с использованием приватного ключа отправителя
        transaction.sign(sender_wallet)
        # Отправка транзакции в блокчейн
        await client.send_transaction(transaction)

    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        # Логирование ошибки
        logger.error(f"Failed to transfer token: {e}\n{detailed_error_traceback}")
        # Дополнительная обработка ошибки, если необходимо
        raise Exception(f"Failed to transfer token: {e}\n{detailed_error_traceback}")


async def get_transaction_history(wallet_address, client):
    try:
        # Получение истории транзакций кошелька
        signature_statuses = await client.get_signatures_for_address(Pubkey(wallet_address))
        # Инициализируем пустой список для хранения истории транзакций
        transaction_history = []
        # Проходим по всем статусам подписей в результате
        for signature_status in signature_statuses['result']:
            # Получаем транзакцию по подписи
            transaction = await client.get_transaction(signature_status['signature'])
            # Добавляем полученную транзакцию в историю транзакций
            transaction_history.append(transaction)

        # Возвращаем список истории транзакций
        return transaction_history

    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        # Логирование ошибки
        logger.error(f"Failed to get transaction history for Solana wallet: {e}\n{detailed_error_traceback}")
        # Дополнительная обработка ошибки, если необходимо
        raise Exception(f"Failed to get transaction history for Solana wallet: {e}\n{detailed_error_traceback}")
