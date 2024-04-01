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

CREATE_WALLET_MESSAGE = {
    "create_wallet": "🔑 Create wallet",
    "wallet_name_prompt": "💼 <b>Please enter the name for your wallet:</b>",
    "wallet_name_confirmation": "💼 <b>Your wallet name:</b> {wallet_name}",
    "wallet_description_prompt": "💬 <b>Now, please enter the description for your wallet:</b>",
    "wallet_created_successfully": "🎉 <b>Wallet created successfully!</b>\n"
                                   "<b><i>Wallet name:</i> {wallet_name}</b>\n"
                                   "<b><i>Wallet description:</i> {wallet_description}</b>\n"
                                   "<b><i>Wallet address:</i> {wallet_address}</b>\n"
                                   "<b><i>Private key:</i> {private_key}</b>\n",
    "continue_message": "➡️ <b>Let's continue!</b>\n<i>Choose an option from the menu:</i>",
    "invalid_wallet_name": "❌ <b>Invalid wallet name entered.</b>\n"
                           "Please enter a valid name for your wallet.",
    "invalid_wallet_description": "❌ <b>Invalid wallet description entered.</b>\n"
                                  "Please enter a valid description for your wallet."
}

# Сообщения для 'connect_wallet'
CONNECT_WALLET_MESSAGE = {
    "connect_wallet_prompt": "<b>🔗 Please enter your Solana wallet address.</b>",
    "connect_wallet": "<b>🔗 Connect wallet</b>",
    "connect_wallet_address_prompt": "<b>🔑 Enter the wallet address to connect to the bot</b>",
    "invalid_wallet_address": "<b>❌ Invalid Solana wallet address</b>",
    "wallet_connected_successfully": "<b>🎉 Wallet with address {wallet_address}</b>\nsuccessfully connected to the bot",
    "invalid_private_key": "<b>❌ Invalid wallet private key</b>",
    "connect_wallet_private_key_prompt": "<b>🔑 Please enter the correct private key of your Solana wallet</b>",
    "this_wallet_already_exists": "<i>This wallet address has already been connected before</i>",
}


# Сообщения для обработки команды balance
BALANCE_MESSAGE = {
    "no_registered_wallet": "<b>🛑 You don't have a registered wallet.</b>\n"
                            "Create a new wallet with the command /create_wallet",
    "balance_success": "<b>💰 Your wallet balance:</b> {balance} SOL"
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
    "transfer_recipient_address_prompt": "<b>📬 Enter the recipient's wallet address:</b>\n"
                                         "Note: The recipient's minimum balance\n"
                                         "should be at least 0.00089784 SOL",
    "transfer_amount_prompt": "<b>💸 Enter the amount of tokens to transfer:</b>",
    "invalid_wallet_address": "<b>❌ Invalid wallet address.</b>",
    "transfer_successful": "<b>✅ Transfer of {amount} SOL to {recipient} successful.</b>",
    "transfer_not_successful": "<b>❌ Failed to transfer {amount} SOL to {recipient}.</b>",
    "insufficient_balance": "<b>❌ Insufficient funds in your wallet for this transfer.</b>",
    "insufficient_balance_recipient": "<b>❌ The recipient's balance\nshould be at least 0.00089784 Sol.</b>",
    "no_wallet_connected": "<b>🔗 Please connect your wallet before transferring tokens.</b>",
    "list_sender_wallets": "<b>📋 Your wallet list:</b>",
    "choose_sender_wallet": "<b>🔑 Enter your wallet address:</b>",
    "invalid_wallet_choice": "<b>❌ Invalid wallet choice.</b>",
    "no_wallets_connected": "<b>❌ You don't have any connected wallets.\n"
                            "Connect a wallet before transferring tokens.</b>",
    "save_new_wallet_prompt": "<b>💾 Save this wallet address:</b> ",
    "wallet_info_template": "{number}) 💼 {name} 📍 {address} 💰 {balance}",
    "save_wallet": "<i>Yes</i>",
    "cancel": "<i>No</i>"
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
