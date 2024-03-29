# solana_wallet_telegram_bot/utils/validators.py

import re

from nacl.public import PublicKey


def is_valid_wallet_name(name):
    pattern = r'^[\w\d\s\-_]+$'
    return bool(re.match(pattern, name))


def is_valid_wallet_description(description):
    # Проверка наличия описания
    if not description.strip():
        return True

    # Проверка максимальной длины описания (например, 500 символов)
    if len(description) > 500:
        return False

    # Регулярное выражение для проверки допустимых символов в описании
    # В данном примере разрешены буквы, цифры, пробелы, знаки препинания и некоторые специальные символы
    pattern = r'^[\w\d\s\-_,.:;!?]*$'

    # Проверка соответствия регулярному выражению
    return bool(re.match(pattern, description))


def is_valid_solana_address(address):
    try:
        PublicKey(address)
        return True
    except ValueError:
        return False
