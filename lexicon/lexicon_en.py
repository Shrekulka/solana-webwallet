# solana_wallet_telegram_bot/pylexicon/lexicon_en.py

# Общие сообщения
GENERAL_MESSAGE = {
    "create_wallet": "🔑 Create wallet",
    "connect_wallet": "🔗 Connect wallet",
    "balance": "💰 Show balance",
    "token_price": "💹 Show token price",
    "token_buy": "💸 Buy token",
    "token_sell": "💳 Sell token",
    "token_transfer": "📲 Transfer token",
    "transaction": "📜 View transaction history",
    "delete_wallet": "🗑️ Delete wallet",
    "settings": "⚙️ Crypto wallet settings",
    "donate": "💝 Donate to the team",
}

# Сообщения для 'connect_wallet'
CREATE_WALLET_MESSAGE = {
    "create_wallet": "🔑 Create wallet",
    "create_wallet_success": "🎉 <b><i>Wallet successfully created!</i></b>\n"
                             "<i>Wallet address:</i> {wallet_address}",
    "wallet_name_prompt": "💼 <b>Please enter the name for your wallet:</b>",
    "wallet_name_confirmation": "💼 <b>Your wallet name:</b> {wallet_name}",
    "wallet_name_confirmation_thanks": "🙏 <b>Thank you!</b>",
    "wallet_description_prompt": "💬 <b>Now, please enter the description for your wallet:</b>",
    "wallet_created_successfully": "💼 <b>Wallet created successfully!</b>\n"
                                   "<b><i>Wallet name:</i> {wallet_name}</b>\n"
                                   "<b><i>Wallet description:</i> {wallet_description}</b>\n"
                                   "<b><i>Wallet address:</i> {wallet_address}</b>",
    "continue_message": "➡️ <b>Let's continue!</b>\n<i>Choose an option from the menu:</i>",
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
START_MESSAGES = {
    "/start": "<b>👋 Hello, {first_name}!</b>\n\n"
              "<i>This bot is designed to work with a wallet on the Solana blockchain.</i>\n"
              "<i>Here you can buy, sell, store, and pay using your wallet.</i>\n"
              "\n\nTo view the list of available commands, type /help 😊",
}

# Справочное сообщение бота
HELP_MESSAGES = {
    "/help": "<b>Available commands:</b>\n\n"
             "💰 <b>balance</b> - show balance...\n\n"
             "📜 <b>transactions</b> - view transaction history...\n\n"
             "💸 <b>send</b> - send coins...\n\n"
             "📥 <b>receive</b> - receive coins...\n\n"
             "🗑️ <b>delete_wallet</b> - delete wallet...\n",
    "start_message_continue": "<b>Continue further!</b>\nChoose a menu item:",
}

# Объединение всех сообщений в словарь LEXICON
LEXICON: dict[str, str] = {**GENERAL_MESSAGE, **CREATE_WALLET_MESSAGE, **CONNECT_WALLET_MESSAGE, **BALANCE_MESSAGE,
                           **TOKEN_PRICE_MESSAGE, **TOKEN_BUY_MESSAGE, **TOKEN_SELL_MESSAGES, **TOKEN_TRANSFER_MESSAGE,
                           **TOKEN_TRANSACTION_MESSAGE, **START_MESSAGES, **HELP_MESSAGES}
