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
# http_client = AsyncClient("https://api.devnet.solana.com")
http_client = AsyncClient('https://api.testnet.solana.com')


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


def is_valid_amount(amount: str | int | float) -> bool:
    if isinstance(amount, (int, float)):
        return True
    try:
        float_amount = float(amount)
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


async def get_transaction_history(wallet_address, client):
    try:
        # Получение истории транзакций кошелька
        signature_statuses = (
            await client.get_signatures_for_address(Pubkey.from_string(wallet_address), limit=1)
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


######################################
# async def get_transaction_history(wallet_address, client):
#     try:
#         # Инициализация клиента
#         async with AsyncClient('https://api.testnet.solana.com') as client:
#             # Получение истории транзакций кошелька
#             signature_statuses = (
#                 await client.get_signatures_for_address(Pubkey.from_string(wallet_address), limit=1)
#             ).value
#             transaction_history = []

#             # Проходим по всем статусам подписей в результате
#             for signature_status in signature_statuses:
#                 # Получаем транзакцию по подписи
#                 transaction = (await client.get_transaction(signature_status.signature)).value
#                 # Добавляем полученную транзакцию в историю транзакций
#                 transaction_history.append(transaction)

#             # Возвращаем список истории транзакций
#             return transaction_history

#     except Exception as e:
#         detailed_error_traceback = traceback.format_exc()
#         # Логирование ошибки
#         logger.error(f"Failed to get transaction history for Solana wallet: {e}\n{detailed_error_traceback}")
#         # Дополнительная обработка ошибки, если необходимо
#         raise Exception(f"Failed to get transaction history for Solana wallet: {e}\n{detailed_error_traceback}")
