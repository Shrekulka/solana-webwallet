# solana_wallet_telegram_bot/pylexicon/lexicon_en.py

# Общие сообщения
GENERAL_MESSAGE = {
    "create_wallet": "Create wallet",
    "connect_wallet": "Connect wallet",
    "balance": "Show balance",
    "token_price": "Show price token",
    "token_buy": "Buy token",
    "token_sell": "Sell token",
    "token_transfer": "Transfer token",
    "transaction": "View transaction history",
    "delete_wallet": "Delete wallet",
    "settings": "Crypto wallet settings",
    "donate": "Donate to the team",
}

# Сообщения для 'connect_wallet'
CREATE_WALLET_MESSAGE = {
    "create_wallet": "Create wallet",
    "create_wallet_success": "Wallet successfully created!\n"
                             "Wallet address: {wallet_address}"
}


# Сообщения для 'connect_wallet'
CONNECT_WALLET_MESSAGE = {
    "connect_wallet": "Connect wallet"
}

# Сообщения для обработки команды balance
BALANCE_MESSAGE = {
    "no_registered_wallet": "У вас нет зарегистрированного кошелька. Создайте новый кошелек командой /create_wallet",
    "balance_success": "Баланс вашего кошелька: {balance} SOL"
}

# Сообщения для 'connect_wallet'
TOKEN_PRICE_MESSAGE = {
    "token_price": "Price token"
}

# Сообщения для обработки команды buy_token
TOKEN_BUY_MESSAGE = {
    "input_prompt": "Введите адрес мята токена и количество SOL для покупки "
                    "через пробел (например, 'TokenMintAddress 1.5')",
    "buy_success": "Токены успешно куплены на {amount} SOL"
}

# Сообщения для обработки команды sell_token
TOKEN_SELL_MESSAGES = {
    "input_prompt": "Введите адрес мята токена и количество токенов для "
                    "продажи через пробел (например, 'TokenMintAddress 100')",
    "sell_success": "Токены успешно проданы на {amount} SOL"
}

# Сообщения для переноса
TOKEN_TRANSFER_MESSAGE = {
    "input_prompt": "Введите адрес получателя, адрес мята токена и количество токенов для "
                    "перевода через пробел (например, 'RecipientAddress TokenMintAddress 100')",
    "transfer_success": "Токены успешно переведены на адрес {recipient_address}"
}

# Сообщения для обработки команды transactions
TOKEN_TRANSACTION_MESSAGE = {
    "empty_history": "История транзакций пуста",
    "transaction_info": "Транзакция {transaction_id}:\n"
                        "Отправитель: {sender}\n"
                        "Получатель: {recipient}\n"
                        "Сумма: {amount} лампортов"
}

# Сообщения для старта и справки
START_HELP_MESSAGES = {
    "/start": "<b>👋 Hello, {first_name}!</b>\n\nThis bot is designed to work with a wallet on the Solana blockchain.\n"
              "Here you can buy, sell, store, and pay using your wallet\n"
              "Your multi-currency wallet has been created, and you can start using the system 🛠"
              "\n\nTo view the list of available commands, type /help 😊",

    # Справочное сообщение бота
    "/help": "<b>Available commands:</b>\n\n"
             "💰 balance - show balance...\n\n"
             "📜 transactions - view transaction history...\n\n"
             "💸 send - send coins...\n\n"
             "📥 receive - receive coins...\n\n"
             "🗑️ delete_wallet - delete wallet...\n",
}

# # Сообщения для отправки монет
# SEND_COINS_MESSAGES = {
#     "send": "Send coins",
#     "send_prompt": "Введите адрес получателя и сумму через пробел (например, 'AdressPOLUchatelya 1.5')",
#     "send_success": "Транзакция на {amount} SOL успешно отправлена на адрес {recipient_address}",
#     "send_invalid_format": "Некорректный формат суммы",
#     "no_wallet": "У вас нет зарегистрированного кошелька. Создайте новый кошелек командой /create_wallet",
# }

# Объединение всех сообщений в словарь LEXICON
LEXICON: dict[str, str] = {**GENERAL_MESSAGE, **CREATE_WALLET_MESSAGE, **CONNECT_WALLET_MESSAGE, **BALANCE_MESSAGE,
                           **TOKEN_PRICE_MESSAGE, **TOKEN_BUY_MESSAGE, **TOKEN_SELL_MESSAGES, **TOKEN_TRANSFER_MESSAGE,
                           **TOKEN_TRANSACTION_MESSAGE, **START_HELP_MESSAGES}
