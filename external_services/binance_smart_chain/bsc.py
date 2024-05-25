import time
import traceback
from typing import Tuple, Dict, List, Optional, Any

import asyncio
from web3 import Web3, AsyncWeb3
# from web3.exceptions import TransactionNotFound
from eth_account import Account

from config_data.config import (BINANCE_NODE_URL, WEI_TO_BNB_RATIO, PRIVATE_KEY_HEX_LENGTH,
                                PRIVATE_KEY_BINARY_LENGTH, timeout_settings)
from logger_config import logger

w3 = AsyncWeb3()
bsc_client = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(BINANCE_NODE_URL))


async def create_bsc_wallet() -> Tuple[str, str, str]:
    """
        Generate a new BSC wallet.

        Returns:
            Tuple[str, str, str]: A tuple containing the public address and private key of the generated wallet.

        Raises:
            Exception: If there's an error during the wallet creation process.
    """
    try:
        bsc_derivation_path = "m/44'/60'/0'/0/0"
        # The use of the Mnemonic features of Account is disabled by default until its API stabilizes.
        # To use these features, please enable them by running `Account.enable_unaudited_hdwallet_features()` and try again.
        Account.enable_unaudited_hdwallet_features()
        #TODO: BNB 24-word mnemonic and derivation path: https://docs.bnbchain.org/docs/learn/genesis/
        # we use 12-word
        acct, mnemonic = Account.create_with_mnemonic(
            passphrase='',
            num_words=12,
            language='english',
            account_path=bsc_derivation_path,
        )

        print(f'new mnemonic: {mnemonic}')
        private_key = w3.to_hex(acct.key)
        print(f'new private_key: {private_key}')
        wallet_address = acct.address
        print(f'new address: {wallet_address}')
        print('**********')

        return wallet_address, private_key, mnemonic, bsc_derivation_path

    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"Failed to create BSC wallet: {e}\n{detailed_error_traceback}")
        # Поднятие нового исключения с подробной информацией
        raise Exception(f"Failed to create BSC wallet: {e}")


def is_valid_bsc_wallet_address(address: str) -> bool:
    """
        Checks whether the input string is a valid Solana wallet address.

        Args:
            address (str): A string containing the presumed wallet address.

        Returns:
            bool: True if the address is valid, False otherwise.
    """
    try:
        # if address.startswith("0x") and len(address) == 42:
        #     if AsyncWeb3.is_checksum_address(address):
        #         return True
        # return False
        return AsyncWeb3.is_address(address)
    except ValueError:
        # Если возникает ошибка, значит адрес невалиден, возвращаем False
        return False


async def get_bnb_balance(wallet_addresses, client):
    """
        Asynchronously retrieves the BNB balance for the specified wallet addresses.

        Args:
            wallet_addresses (Union[str, List[str]]): The wallet address or a list of wallet addresses.
            client: The BSC client.

        Returns:
            Union[float, List[float]]: The BNB balance or a list of BNB balances corresponding to the wallet addresses.
    """
    try:
        # Если передан одиночный адрес кошелька
        if isinstance(wallet_addresses, str):
            balance = await client.eth.get_balance(w3.to_checksum_address(wallet_addresses))
            # Преобразование wei в BNB
            bnb_balance = balance / WEI_TO_BNB_RATIO
            logger.debug(
                f"wallet_address: {wallet_addresses}, balance: {balance:_}, bnb_balance: {bnb_balance}"
            )
            return bnb_balance
        # Если передан список адресов кошельков
        elif isinstance(wallet_addresses, list):
            bnb_balances = []
            for address in wallet_addresses:
                balance = await client.eth.get_balance(w3.to_checksum_address(address))
                # Преобразование wei в BNB
                bnb_balance = balance / WEI_TO_BNB_RATIO
                bnb_balances.append(bnb_balance)
            return bnb_balances
        else:
            raise ValueError(
                "Invalid type for wallet_addresses. Expected str or list[str]."
            )
    except Exception as error:
        detailed_error_traceback = traceback.format_exc()
        logger.error(
            f"Failed to get BNB balance: {error}\n{detailed_error_traceback}")
        raise Exception(
            f"Failed to get BNB balance: {error}\n{detailed_error_traceback}")


def is_valid_bsc_private_key(private_key: str) -> bool:
    """
        Checks whether the input string is a valid BSC private key.

        Args:
            private_key (str): A string containing the presumed private key.

        Returns:
            bool: True if the private key is valid, False otherwise.
    """
    try:
        # TODO: надо сделать проверку на валидность для private_key
        # Проверяем длину приватного ключа BSC
        # Если длина ключа 64 символа, это hex-представление
        if len(private_key) == PRIVATE_KEY_HEX_LENGTH:
            print('****** PRIVATE_KEY_HEX_LENGTH')
        # Если длина ключа 32 символа, это представление в бинарном формате
        elif len(private_key) == PRIVATE_KEY_BINARY_LENGTH:
            print('****** PRIVATE_KEY_BINARY_LENGTH')
        else:
            # Если длина ключа не соответствует ожидаемой длине, возвращаем False
            print('******** длина ключа не соответствует ожидаемой длине')
            return False
        # Если создание объекта Keypair прошло успешно, значит приватный ключ валиден
        return True
    except ValueError:
        # Если возникает ошибка, значит приватный ключ невалиден, возвращаем False
        return False


def get_bsc_wallet_address_from_private_key(private_key: str) -> str:
    """
        Gets the wallet address from the private key.

        Args:
            private_key (str): A string containing the presumed private key.

        Returns:
            str: The wallet address as a string.
    """
    account_from_key = Account.from_key(private_key)
    wallet_address = account_from_key.address
    # Возвращение адреса кошелька в виде строки
    return wallet_address


def is_valid_amount(amount: str | int | float) -> bool:
    """
        Checks if the value is a valid amount.

        Arguments:
        amount (str | int | float): The value of the amount to be checked.

        Returns:
        bool: True if the amount value is valid, False otherwise.
    """
    # Проверяем, является ли аргумент amount экземпляром int или float.
    if isinstance(amount, (int, float)):
        return True
        # Если amount не является int или float, пытаемся преобразовать его в float.
    try:
        float(amount)
        return True
    except ValueError:
        return False


async def bsc_transfer_token(sender_address: str, sender_private_key: str, recipient_address: str, amount: float,
                             client: AsyncWeb3) -> bool:
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
    if not is_valid_bsc_wallet_address(sender_address):
        raise ValueError("Invalid sender address")

    # Проверяем, является ли адрес получателя действительным
    if not is_valid_bsc_wallet_address(recipient_address):
        raise ValueError("Invalid recipient address")

    # Проверяем, является ли приватный ключ отправителя действительным
    if not is_valid_bsc_private_key(sender_private_key):
        raise ValueError("Invalid sender private key")

    print('******** amount: ', amount)

    if not is_valid_amount(amount):
        raise ValueError("Invalid amount")

    wei_amount = AsyncWeb3.to_wei(amount, 'ether')
    print('******** wei_amount:', wei_amount)
    nonce = await client.eth.get_transaction_count(sender_address)
    print('****** nonce: ', nonce)
    gas_price = await client.eth.gas_price
    print('**** gas_price:', gas_price)

    # 1. Build a new tx
    transaction = {
        'from': sender_address,
        'to': recipient_address,
        'value': wei_amount,
        'nonce': nonce,
        'gas': 2000000,
        'gasPrice': gas_price,
        # 'maxFeePerGas': 2000000000,
        # 'maxPriorityFeePerGas': 1000000000,
    }

    # Подписываем транзакцию с приватным ключом
    signed_txn = client.eth.account.sign_transaction(transaction, sender_private_key)
    print('******* signed_txn:', signed_txn)

    # Отправка транзакции
    txn_hash = await client.eth.send_raw_transaction(signed_txn.rawTransaction)
    print('***** txn_hash.hex(): ', txn_hash.hex())
    txn_receipt = None

    try:
        txn_receipt = await client.eth.wait_for_transaction_receipt(txn_hash)
        # for i in range(10):
        #     try:
        #         await asyncio.sleep(i)
        #         txn_receipt = await client.eth.get_transaction_receipt(txn_hash)
        #         break
        #     except TransactionNotFound:
        #         print('******* TransactionNotFound i:', i)
    except Exception as e:
        detailed_error_traceback = traceback.format_exc()
        logger.error(f"BSC, Failed to get transaction receipt: {e}\n{detailed_error_traceback}")
        # Вызываем новое исключения с подробной информацией
        raise Exception(f"BSC, Failed to get transaction receipt: {e}")

    print('******** txn_receipt: ', txn_receipt)
    if txn_receipt and hasattr(txn_receipt, 'status'):
        if txn_receipt['status'] == 1:
            return True
    return False
