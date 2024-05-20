# solana-webwallet/utils/validators.py

import re


def is_valid_wallet_name(name: str) -> bool:
    """
        Checks the validity of a wallet name.

        Args:
            name (str): The name of the wallet.

        Returns:
            bool: True if the wallet name is valid, False otherwise.
    """
    # Создаем регулярное выражение для проверки имени кошелька.
    # ^ - начало строки
    # [\w\d\s\-_]+ - один или более символов, которые могут быть буквами, цифрами, пробелами, дефисами или
    # подчеркиваниями
    # $ - конец строки
    pattern = r'^[\w\d\s\-_]+$'
    # Проверка соответствия регулярному выражению
    return bool(re.match(pattern, name))


def is_valid_wallet_description(description: str) -> bool:
    """
        Checks the validity of a wallet description.

        Args:
            description (str): The description of the wallet.

        Returns:
            bool: True if the wallet description is valid, False otherwise.
    """
    # Проверка наличия описания
    if not description.strip():
        return False

    # Проверка максимальной длины описания (например, 500 символов)
    elif len(description) > 500:
        return False

    # Регулярное выражение для проверки допустимых символов в описании
    # В данном примере разрешены буквы, цифры, пробелы, знаки препинания и некоторые специальные символы
    else:
        pattern = r'^[\w\d\s\-_,.:;!?]*$'

        # Проверка соответствия регулярному выражению
        return bool(re.match(pattern, description))


def is_valid_wallet_seed_phrase(seed_phrase: str) -> bool:
    """
        Checks the validity of a wallet seed phrase.

        Args:
            seed_phrase (str): The seed phrase of the wallet.

        Returns:
            bool: True if the wallet seed phrase is valid, False otherwise.
    """
    seed_phrase_list = seed_phrase.strip().split()

    if len(seed_phrase_list) in [12, 24]:
        return True
    else:
        return False
