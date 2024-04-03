# solana_wallet_telegram_bot/external_services/solana/solana.py

import traceback
from typing import Tuple

from solana.rpc.api import Keypair
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solders.pubkey import Pubkey

from solders.system_program import transfer, TransferParams
from solders.transaction_status import TransactionConfirmationStatus

from logger_config import logger

# Создание клиента для подключения к тестовой сети Devnet
# http_client = Client("https://api.devnet.solana.com")
http_client = AsyncClient("https://api.devnet.solana.com")


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

    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Failed to create Solana wallet: {e}\n{detailed_error_traceback}")
        # Поднятие нового исключения с подробной информацией
        raise Exception(f"Failed to create Solana wallet: {e}")


def get_wallet_address_from_private_key(private_key: str) -> str:
    """
        Gets the wallet address from the private key.

        Args:
            private_key (str): A string containing the presumed private key.

        Returns:
            str: The wallet address as a string.
    """
    # Создание объекта Keypair из закрытого ключа, преобразованного из шестнадцатеричной строки в байтовый формат.
    # Метод from_seed используется для создания ключевой пары на основе семени (seed), которое представляет собой
    # закрытый ключ в байтовом формате.
    # Мы используем метод bytes.fromhex для преобразования шестнадцатеричной строки в байтовый формат.
    keypair = Keypair.from_seed(bytes.fromhex(private_key))

    # Получение публичного адреса кошелька из объекта Keypair
    wallet_address = str(keypair.pubkey())

    # Возвращение адреса кошелька в виде строки
    return wallet_address


def is_valid_wallet_address(address: str) -> bool:
    """
        Checks whether the input string is a valid Solana wallet address.

        Args:
            address (str): A string containing the presumed wallet address.

        Returns:
            bool: True if the address is valid, False otherwise.
    """
    try:
        # Создание объекта PublicKey из строки адреса.
        # Метод from_string используется для создания объекта PublicKey из строки, содержащей адрес кошелька.
        # Этот метод позволяет создать объект PublicKey, который может быть использован для проверки подписей
        # или других операций, связанных с публичным ключом кошелька.
        Pubkey.from_string(address)

        # Если создание объекта PublicKey прошло успешно, значит адрес валиден
        return True
    except ValueError:
        # Если возникает ошибка, значит адрес невалиден, возвращаем False
        return False


def is_valid_private_key(private_key: str) -> bool:
    """
        Checks whether the input string is a valid Solana private key.

        Args:
            private_key (str): A string containing the presumed private key.

        Returns:
            bool: True if the private key is valid, False otherwise.
    """
    try:
        # Проверяем длину приватного ключа Solana
        # Если длина ключа 64 символа, это hex-представление
        if len(private_key) == 64:
            # Преобразование строки, содержащей приватный ключ, в байтовый формат с помощью метода fromhex,
            # а затем создание объекта Keypair из этих байтов.
            # Этот метод используется для создания объекта Keypair, который может быть использован для
            # подписывания транзакций или выполнения других операций, связанных с приватным ключом.
            Keypair.from_seed(bytes.fromhex(private_key))
            # Keypair.from_bytes(bytes.fromhex(private_key))
        # Если длина ключа 32 символа, это представление в бинарном формате
        elif len(private_key) == 32:
            # Преобразование строки, содержащей приватный ключ, в байтовый формат с помощью метода fromhex,
            # а затем создание объекта Keypair из этих байтов.
            # Этот метод используется для создания объекта Keypair из приватного ключа с использованием его seed.
            Keypair.from_seed(bytes.fromhex(private_key))
        else:
            # Если длина ключа не соответствует ожидаемой длине, возвращаем False
            return False
        # Если создание объекта Keypair прошло успешно, значит приватный ключ валиден
        return True
    except ValueError:
        # Если возникает ошибка, значит приватный ключ невалиден, возвращаем False
        return False


def is_valid_amount(amount: str | int) -> bool:
    try:
        float(amount)
        return True
    except ValueError:
        return False


async def get_sol_balance(wallet_addresses, client):
    """
    Asynchronously retrieves the SOL balance for the specified wallet addresses.

    Args:
        wallet_addresses (Union[str, List[str]]): The wallet address or a list of wallet addresses.
        client: The Solana client.

    Returns:
        Union[float, List[float]]: The SOL balance or a list of SOL balances corresponding to the wallet addresses.
    """
    try:
        # Если передан одиночный адрес кошелька
        if isinstance(wallet_addresses, str):
            balance = (await client.get_balance(Pubkey.from_string(wallet_addresses))).value
            # Преобразование лампортов в SOL
            sol_balance = balance / 10 ** 9
            logger.debug(f"wallet_address: {wallet_addresses}, balance: {balance}, sol_balance: {sol_balance}")
            return sol_balance
        # Если передан список адресов кошельков
        elif isinstance(wallet_addresses, list):
            sol_balances = []
            for address in wallet_addresses:
                balance = (await client.get_balance(Pubkey.from_string(address))).value
                # Преобразование лампортов в SOL
                sol_balance = balance / 10 ** 9
                sol_balances.append(sol_balance)
            return sol_balances
        else:
            raise ValueError("Invalid type for wallet_addresses. Expected str or list[str].")
    except Exception as error:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Failed to get Solana balance: {error}\n{detailed_error_traceback}")
        raise Exception(f"Failed to get Solana balance: {error}\n{detailed_error_traceback}")


async def transfer_token(sender_address: str, sender_private_key: str, recipient_address: str, amount: float,
                         client: AsyncClient) -> bool:
    """
        Asynchronous function to transfer tokens between wallets.

        Args:
            sender_address (str): Sender's address.
            sender_private_key (str): Sender's private key.
            recipient_address (str): Recipient's address.
            amount (float): Amount of tokens to transfer.
            client (AsyncClient): Asynchronous client for sending the transaction.

        Raises:
            ValueError: If any of the provided addresses is invalid or the private key is invalid.

        Returns:
            bool: True if the transfer is successful, False otherwise.
    """
    # Проверяем, является ли адрес отправителя действительным
    if not is_valid_wallet_address(sender_address):
        raise ValueError("Invalid sender address")

    # Проверяем, является ли адрес получателя действительным
    if not is_valid_wallet_address(recipient_address):
        raise ValueError("Invalid recipient address")

    # Проверяем, является ли приватный ключ отправителя действительным
    if not is_valid_private_key(sender_private_key):
        raise ValueError("Invalid sender private key")

    if not is_valid_amount(amount):
        raise ValueError("Invalid amount")

    # Создаем пару ключей отправителя из приватного ключа
    sender_keypair = Keypair.from_seed(bytes.fromhex(sender_private_key))

    # Создаем транзакцию для перевода токенов
    txn = Transaction().add(
        transfer(
            TransferParams(
                from_pubkey=sender_keypair.pubkey(),
                to_pubkey=Pubkey.from_string(recipient_address),
                # Количество лампортов для перевода, преобразованное из суммы SOL.
                lamports=int(amount * 10 ** 9),
            )
        )
    )
    # Отправляем транзакцию клиенту
    send_transaction_response = await client.send_transaction(txn, sender_keypair)
    # Подтверждаем транзакцию
    confirm_transaction_response = await client.confirm_transaction(send_transaction_response.value)

    if hasattr(confirm_transaction_response, 'value') and confirm_transaction_response.value[0]:
        if hasattr(confirm_transaction_response.value[0], 'confirmation_status'):
            confirmation_status = confirm_transaction_response.value[0].confirmation_status
            if confirmation_status:
                logger.debug(f"Transaction confirmation_status: {confirmation_status}")
                if confirmation_status in [TransactionConfirmationStatus.Confirmed,
                                           TransactionConfirmationStatus.Finalized]:
                    return True
    return False


######################################
async def get_transaction_history(wallet_address, client):
    try:
        # Инициализация клиента
        async with AsyncClient('https://api.testnet.solana.com') as client:
            # Получение истории транзакций кошелька
            signature_statuses = (
                await client.get_signatures_for_address(Pubkey(wallet_address), limit=1)
            ).value
            transaction_history = []

            # Проходим по всем статусам подписей в результате
            for signature_status in signature_statuses:
                # Получаем транзакцию по подписи
                transaction = (await client.get_transaction(signature_status.signature)).value
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

# TODO: часто ломается
# async def get_transaction_history(wallet_address, client):
#     try:
#         #### test: с этой нодой меньше ошибок
#         # client = Client('https://api.testnet.solana.com')
#         client = AsyncClient('https://api.testnet.solana.com')
#         #### test
#
#         # Получение истории транзакций кошелька
#         # signature_statuses = client.get_signatures_for_address(Pubkey.from_string(wallet_address))
#         # signature_statuses = (await client.get_signatures_for_address(Pubkey.from_string(wallet_address), limit=1)).value
#         signature_statuses = (
#             await client.get_signatures_for_address(Pubkey.from_string(wallet_address), limit=1)).value
#         transaction_history = []
#
#         # Проходим по всем статусам подписей в результате
#         # for signature_status in signature_statuses.value:
#         for signature_status in signature_statuses:
#             print('signature_status: ', signature_status)
#             # Получаем транзакцию по подписи
#             # transaction = client.get_transaction(signature_status.signature)
#             transaction = (await client.get_transaction(signature_status.signature)).value
#             # Добавляем полученную транзакцию в историю транзакций
#             transaction_history.append(transaction)
#
#         # # Возвращаем список истории транзакций
#         return transaction_history
#
#     except Exception as e:
#         detailed_error_traceback = traceback.format_exc()
#         # Логирование ошибки
#         logger.error(f"Failed to get transaction history for Solana wallet: {e}\n{detailed_error_traceback}")
#         # Дополнительная обработка ошибки, если необходимо
#         raise Exception(f"Failed to get transaction history for Solana wallet: {e}\n{detailed_error_traceback}")

#############################################################

# async def transfer_token(sender_address: str, sender_private_key: str, recipient_address: str, amount: float,
#                          client: AsyncClient) -> None:
#     try:
#         # Проверяем валидность адреса отправителя
#         if not is_valid_wallet_address(sender_address):
#             raise ValueError("Неверный адрес отправителя")

#         # Проверяем валидность адреса получателя
#         if not is_valid_wallet_address(recipient_address):
#             raise ValueError("Неверный адрес получателя")

#         # Проверяем валидность приватного ключа отправителя
#         if not is_valid_private_key(sender_private_key):
#             raise ValueError("Неверный приватный ключ отправителя")

#         # Создаем ключевую пару отправителя из приватного ключа
#         sender_keypair = Keypair.from_seed(bytes.fromhex(sender_private_key))

#         # Получаем публичный ключ получателя из его адреса
#         recipient_pubkey = Pubkey(bytes(recipient_address, 'utf-8'))

#         # Преобразуем сумму перевода из SOL в лампорты
#         lamports = int(amount * 10 ** 9)

#         # Получаем последний хеш блока для использования в транзакции
#         blockhash_bytes = bytes((await client.get_latest_blockhash()).value)
#         blockhash = Hash(blockhash_bytes)

#         # Создаем инструкцию перевода
#         ix = transfer(
#             TransferParams(
#                 from_pubkey=sender_keypair.pubkey(),  # Публичный ключ отправителя из ключевой пары отправителя
#                 to_pubkey=recipient_pubkey,  # Публичный ключ получателя
#                 lamports=lamports, ))  # Количество лампортов для перевода

#         # Создаем сообщение для транзакции, используя версию 0 (V0) сообщения.
#         # Это сообщение будет содержать следующие параметры:
#         # - Отправитель: публичный ключ отправителя из ключевой пары отправителя.
#         # - Инструкции: список инструкций, в данном случае, только одна инструкция перевода (ix).
#         # - Адреса учетных записей для поиска: пустой список, так как нет необходимости в дополнительных адресах.
#         # - Хэш блока: последний хэш блока, используемый в транзакции для обеспечения ее уникальности и подтверждения.
#         message = MessageV0.try_compile(sender_keypair.pubkey(), [ix], [], blockhash)

#         # Создаем транзакцию, используя сообщение и добавляя ключевую пару отправителя в качестве подписчика.
#         # Транзакция будет подписана ключевой парой отправителя перед отправкой в сеть.
#         tx = VersionedTransaction(message, [sender_keypair])

#         # Создаем объект опций транзакции, устанавливая параметр skip_confirmation в False,
#         # чтобы не пропускать подтверждение транзакции перед ее выполнением.
#         tx_opts = TxOpts(skip_confirmation=False)

#         # Отправляем подписанную транзакцию в сеть с использованием асинхронного клиента.
#         # Передаем транзакцию (tx) и опции транзакции (tx_opts) в метод send_transaction.
#         await client.send_transaction(tx, opts=tx_opts)

#     except ValueError as e:
#         # Логируем ошибку в случае неверных данных
#         logger.error(f"Error during token transfer: {e}")

#     except Exception as e:
#         # Логируем другие исключения
#         detailed_error_traceback = traceback.format_exc()
#         logger.error(f"Error during token transfer: {e}\n{detailed_error_traceback}")

# ###############################################
# async def get_token_price(token_mint_address):
#     # Формирование URL для запроса цены токена к внешнему API - надо доработать
#     api_url = f"https://api.example.com/token-prices/{token_mint_address}"
#     try:
#         # Отправка GET запроса к API для получения информации о цене токена
#         response = requests.get(api_url)
#         # Проверка на наличие ошибок HTTP
#         response.raise_for_status()
#         # Преобразование ответа в формат JSON
#         token_data = response.json()
#         # Извлечение цены токена из полученных данных
#         token_price = token_data["price"]
#
#         # Возвращение цены токена
#         return token_price
#
#     # Обработка ошибок запроса (например, проблемы с сетью)
#     except requests.RequestException as e:
#         logger.error(f"Failed to fetch token price: {e}")
#         detailed_error_traceback = traceback.format_exc()
#         raise Exception(f"Failed to fetch token price: {e}\n{detailed_error_traceback}")
#     # Обработка неправильного формата ответа от API (отсутствует ключ 'price')
#     except KeyError:
#         logger.error("Invalid response format: missing 'price' key")
#         detailed_error_traceback = traceback.format_exc()
#         raise Exception(f"Invalid response format: missing 'price' key\n{detailed_error_traceback}")
#
#
# async def buy_token(wallet, token_mint_address, amount, client):
#     try:
#         # Получение ассоциированного токенового аккаунта для указанного кошелька
#         associated_token_account = get_associated_token_address(wallet.public_key(), token_mint_address)
#
#         # Получение информации о токеновом аккаунте
#         account_info = await client.get_account_info(associated_token_account)
#         # Если ассоциированный токеновый аккаунт не существует
#         if account_info is None:
#             # Создание объекта транзакции для выполнения операции покупки токенов
#             transaction = Transaction()
#             # Создание инструкции для создания ассоциированного токенового аккаунта
#             create_account_instruction = create_associated_token_account(
#                 # Оплата комиссии за создание аккаунта происходит с кошелька отправителя
#                 payer=wallet.public_key(),
#                 # Владелец создаваемого аккаунта - также кошелек отправителя
#                 owner=wallet.public_key(),
#                 # Адрес монетного токена, для которого создается ассоциированный аккаунт
#                 mint=token_mint_address, )
#
#             # Добавление инструкции создания ассоциированного токенового аккаунта к транзакции.
#             transaction.add(create_account_instruction)
#             # Подписание транзакции с использованием приватного ключа кошелька.
#             transaction.sign(wallet)
#             # Отправка подписанной транзакции в блокчейн.
#             await client.send_transaction(transaction)
#
#         # Получение информации о цене токена с внешнего API
#         token_price = await get_token_price(token_mint_address)
#
#         # Вычисление количества токенов, которое можно купить на указанную сумму SOL
#         sol_amount = amount / token_price
#         # Преобразование в мелкие единицы
#         token_amount = int(sol_amount * 10 ** 9)
#
#         # Параметры для выполнения транзакции покупки токенов.
#         transfer_params = TransferCheckedParams(
#             # Количество токенов для покупки, выраженное в мелких единицах.
#             amount=token_amount,
#             # Количество десятичных знаков токена.
#             decimals=6,
#             # Адрес целевого токенового аккаунта, куда будут отправлены купленные токены.
#             dest=associated_token_account,
#             # Адрес монетного токена.
#             mint=token_mint_address,
#             # Публичный ключ владельца кошелька, который покупает токены.
#             owner=wallet.public_key(),
#             # Идентификатор программы для работы с токенами.
#             program_id=TOKEN_PROGRAM_ID,
#             # Источник токенов, который указывается как публичный ключ кошелька.
#             source=wallet.public_key(), )
#         # Создание инструкции для выполнения проверенной транзакции покупки токенов.
#         transfer_instruction = transfer_checked(transfer_params)
#
#         # Создание новой транзакции.
#         transaction = Transaction()
#         # Добавление инструкции перевода токенов в созданную транзакцию.
#         transaction.add(transfer_instruction)
#         # Подписание транзакции с использованием приватного ключа кошелька отправителя.
#         transaction.sign(wallet)
#         # Отправка подписанной транзакции в сеть блокчейна.
#         await client.send_transaction(transaction)
#
#     except Exception as e:
#         detailed_error_traceback = traceback.format_exc()
#         # Логирование ошибки
#         logger.error(f"Failed to buy token: {e}\n{detailed_error_traceback}")
#         # Дополнительная обработка ошибки, если необходимо
#         raise Exception(f"Failed to buy token: {e}\n{detailed_error_traceback}")
#
#
# async def sell_token(wallet, token_mint_address, amount, client):
#     try:
#         # Получение ассоциированного токенового аккаунта для указанного кошелька и мята
#         associated_token_account = get_associated_token_address(wallet.public_key(), token_mint_address)
#
#         # Получение информации о цене токена с внешнего API
#         token_price = await get_token_price(token_mint_address)
#
#         # Вычисление суммы SOL, которую можно получить за указанное количество токенов
#         sol_amount = amount * token_price
#
#         # Параметры для выполнения проверенной транзакции продажи токенов.
#         transfer_params = TransferCheckedParams(
#             # Количество токенов для продажи, выраженное в мелких единицах.
#             amount=int(amount * 10 ** 9),
#             # Количество десятичных знаков токена.
#             decimals=6,
#             # Публичный ключ кошелька, на который будут отправлены вырученные средства от продажи токенов.
#             dest=wallet.public_key(),
#             # Адрес монетного токена.
#             mint=token_mint_address,
#             # Публичный ключ владельца токенов, который продает токены.
#             owner=associated_token_account,
#             # Идентификатор программы для работы с токенами.
#             program_id=TOKEN_PROGRAM_ID,
#             # Источник токенов, который указывается как публичный ключ ассоциированного токенового аккаунта.
#             source=associated_token_account,
#         )
#
#         # Создание инструкции для выполнения проверенной транзакции продажи токенов.
#         transfer_instruction = transfer_checked(transfer_params)
#
#         # Создание новой транзакции.
#         transaction = Transaction()
#         # Добавление инструкции перевода токенов в созданную транзакцию.
#         transaction.add(transfer_instruction)
#         # Подписание транзакции с использованием приватного ключа кошелька отправителя.
#         transaction.sign(wallet)
#         # Отправка подписанной транзакции в сеть блокчейна.
#         await client.send_transaction(transaction)
#
#         # Создание параметров для перевода SOL.
#         transfer_params = TransferParams(
#             # Публичный ключ отправителя SOL.
#             from_pubkey=wallet.public_key(),
#             # Публичный ключ получателя SOL, который является таким же, как и отправитель, так как SOL переводится на
#             # тот же кошелек.
#             to_pubkey=wallet.public_key(),
#             # Количество лампортов для перевода, преобразованное из суммы SOL.
#             lamports=int(sol_amount * 10 ** 9),
#         )
#         # Создание инструкции перевода SOL с использованием параметров перевода.
#         transfer_instruction = transfer(transfer_params)
#
#         # Создание новой транзакции.
#         transaction = Transaction()
#         # Добавление инструкции перевода SOL в созданную транзакцию.
#         transaction.add(transfer_instruction)
#         # Отправка транзакции в блокчейн через клиент.
#         await client.send_transaction(transaction)
#
#     except Exception as e:
#         detailed_error_traceback = traceback.format_exc()
#         # Логирование ошибки
#         logger.error(f"Failed to sell token: {e}\n{detailed_error_traceback}")
#         # Дополнительная обработка ошибки, если необходимо
#         raise Exception(f"Failed to sell token: {e}\n{detailed_error_traceback}")

#
# async def get_transaction_history(wallet_address, client):
#     try:
#         # Получение истории транзакций кошелька
#         signature_statuses = await client.get_signatures_for_address(Pubkey(wallet_address))
#         # Инициализируем пустой список для хранения истории транзакций
#         transaction_history = []
#         # Проходим по всем статусам подписей в результате
#         for signature_status in signature_statuses['result']:
#             # Получаем транзакцию по подписи
#             transaction = await client.get_transaction(signature_status['signature'])
#             # Добавляем полученную транзакцию в историю транзакций
#             transaction_history.append(transaction)
#
#         # Возвращаем список истории транзакций
#         return transaction_history
#
#     except Exception as e:
#         detailed_error_traceback = traceback.format_exc()
#         # Логирование ошибки
#         logger.error(f"Failed to get transaction history for Solana wallet: {e}\n{detailed_error_traceback}")
#         # Дополнительная обработка ошибки, если необходимо
#         raise Exception(f"Failed to get transaction history for Solana wallet: {e}\n{detailed_error_traceback}")
