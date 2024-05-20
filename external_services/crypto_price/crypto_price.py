# solana_wallet_telegram_bot/external_services/crypto_price/crypto_price.py

import ccxt

from config_data.config import CRYPTO_EXCHANGES


async def get_crypto_prices(crypto_symbol: str) -> dict:
    """
        Fetches cryptocurrency prices from various exchanges.

        Args:
        crypto_symbol (str): The symbol of the cryptocurrency, for example, BTC for Bitcoin.

        Returns:
        dict: A dictionary where keys are exchange names and values are dictionaries containing cryptocurrency price
              data.
        Each dictionary contains a key "last_price" with the last known price of the cryptocurrency on that exchange.

        Raises:
        Errors that may occur when accessing the exchange API or processing data:
        - ccxt.NetworkError: Network error when accessing the exchange API.
        - ccxt.ExchangeError: Error processing the request to the exchange API.
        - ccxt.BaseError: Error related to the ccxt library.
        - Exception: Any other error that may occur during the execution of the function.
    """
    # Словарь для хранения цен на криптовалюту на различных биржах
    prices = {}

    # Валюта, в которой мы хотим получить цены (USDT)
    currency = "USDT"

    # Итерируемся по каждой бирже
    for exchange_name in CRYPTO_EXCHANGES:
        # Получаем объект биржи из ccxt по имени
        exchange = getattr(ccxt, exchange_name)()
        # Инициализируем пустой словарь для цены на текущей бирже
        prices[exchange_name] = {}

        try:
            # Формируем символ криптовалюты в соответствии с требованиями каждой биржи
            symbol = f"{crypto_symbol}/{currency}"
            # Для KuCoin необходимо заменить "/" на "-"
            if exchange_name == "kucoin":
                symbol = symbol.replace("/", "-")

            # Получаем данные о тикере (цене) криптовалюты с биржи
            ticker = exchange.fetch_ticker(symbol)
            # Получаем последнюю цену тикера
            last_price = ticker["last"]
            # Выводим информацию о цене криптовалюты на текущей бирже
            print(f"Price of {crypto_symbol} on {exchange_name}: {last_price}")
            # Сохраняем последнюю цену криптовалюты для текущей биржи
            prices[exchange_name]["last_price"] = last_price
        except Exception as e:
            # В случае ошибки при получении цены, логируем её
            print(f"Error fetching price for {symbol} on {exchange_name}: {e}")

    # Возвращаем словарь с ценами криптовалюты на различных биржах
    return prices
