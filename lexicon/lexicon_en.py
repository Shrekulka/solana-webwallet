# solana_wallet_telegram_bot/pylexicon/lexicon_en.py


MAIN_MENU_BUTTONS: dict[str, str] = {
    "create_wallet": "🔑 Create wallet",
    "connect_wallet": "🔗 Connect wallet",
    "balance": "💰 Show balance",
    "token_price": "💹 Show token price",
    "token_buy": "💸 Buy token",
    "token_sell": "💳 Sell token",
    # "token_transfer": "📲 Transfer token",
    "token_transfer": "📲 Send token",
    "transaction": "📜 View transaction history",
    "delete_wallet": "🗑️ Delete wallet",
    "settings": "⚙️ Crypto wallet settings",
    "donate": "💝 Donate to the team",
}

OTHER_BUTTONS: dict[str, str] = {
    "button_back": "⬅️ back",
    "back_to_main_menu": "<b>🏠 Main menu</b>\n\n"
                         "To view the list of available commands, type /help 😊",
}

GENERAL_MESSAGE: dict[str, str] = {
    "unexpected_input": "❌ <b>Unexpected input</b>\n\n"
                        "Please select an action from the menu\n"
                        "or enter one of the available commands,\n"
                        "such as /start or /help.",
}
CREATE_WALLET_MESSAGE = {
    "create_name_wallet": "💼 <b>Please enter the name for your wallet:</b>",
    "wallet_name_confirmation": "💼 <b>Your wallet name:</b> {wallet_name}",
    "create_description_wallet": "💬 <b>Now, please enter the description for your wallet:</b>",
    "wallet_created_successfully": "🎉 <b>Wallet created successfully!</b>\n"
                                   "<b><i>Wallet name:</i> {wallet_name}</b>\n"
                                   "<b><i>Wallet description:</i> {wallet_description}</b>\n"
                                   "<b><i>Wallet address:</i> {wallet_address}</b>\n"
                                   "<b><i>Private key:</i> {private_key}</b>\n",
    "invalid_wallet_name": "❌ <b>Invalid wallet name entered.</b>\n"
                           "Please enter a valid name for your wallet.",
    "invalid_wallet_description": "❌ <b>Invalid wallet description entered.</b>\n"
                                  "Please enter a valid description for your wallet.",
    "create_new_name_wallet": "💼 <b>Enter a new name for the connected wallet:</b>",
}

# Сообщения для 'connect_wallet'
CONNECT_WALLET_MESSAGE = {
    "connect_wallet_address": "<b>🔑 Enter the wallet address to connect to the bot</b>",
    "connect_wallet_add_name": "<b>💼 Please enter name of your wallet</b>",
    "connect_wallet_add_description": "💬 <b>Now, please enter the description for your wallet:</b>",
    "invalid_wallet_address": "<b>❌ Invalid wallet address</b>",
    "wallet_connected_successfully": "<b>🎉 Wallet with address:</b>\n"
                                     "<b><i>{wallet_address}</i></b>\n"
                                     "<b>successfully connected to the bot!</b>",
    "this_wallet_already_exists": "<i>This wallet address has already been connected before</i>",
}

# Сообщения для обработки команды balance
BALANCE_MESSAGE = {
    "no_registered_wallet": "<b>🛑 You don't have a registered wallet.</b>",
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
TOKEN_TRANSFER_TRANSACTION_MESSAGE = {
    "transfer_recipient_address_prompt": "<b>📬 Enter the recipient's wallet address:</b>\n\n"
                                         "Note: The recipient's minimum balance\n"
                                         "should be at least 0.00089784 SOL",
    "transfer_amount_prompt": "<b>💸 Enter the amount of tokens to transfer:</b>",
    "invalid_wallet_address": "<b>❌ Invalid wallet address.</b>",
    "transfer_successful": "<b>✅ Transfer of {amount} SOL\nto {recipient}\nsuccessful.</b>",
    "transfer_not_successful": "<b>❌ Failed to transfer {amount} SOL to {recipient}.</b>",
    "insufficient_balance": "<b>❌ Insufficient funds in your wallet for this transfer.</b>",
    "insufficient_balance_recipient": "<b>❌ The recipient's balance\nshould be at least 0.00089784 Sol.</b>",
    "no_wallet_connected": "<b>🔗 Please connect your wallet before transferring tokens.</b>",
    "list_sender_wallets": "<b>📋 Your wallet list:</b>\n\nClick on the relevant wallet:",
    "choose_sender_wallet": "<b>🔑 Enter your wallet address:</b>",
    "invalid_wallet_choice": "<b>❌ Invalid wallet choice.</b>",
    "no_wallets_connected": "<b>❌ You don't have any connected wallets.\n"
                            "Connect a wallet before transferring tokens.</b>",
    "save_new_wallet_prompt": "<b>💾 Save this wallet address:</b> ",
    "wallet_info_template": "{number}) 💼 {name} 📍 {address} 💰 {balance}",
    "save_wallet": "<i>Yes</i>",
    "cancel": "<i>No</i>",
    "invalid_amount": "<b>❌ Invalid amount.</b>",
    "transfer_sender_private_key_prompt": "<b>Enter private key for this wallet:</b>",
    "invalid_private_key": "<b>❌ Invalid private key.</b>",
    "empty_history": "😔 Transaction history is empty.",
    "server_unavailable": "The server is currently unavailable. Please try again later.",
    "transaction_info": "<b>💼 Transaction:</b> {transaction_id}:\n"
                        "<b>📲 Sender:</b> {sender}\n"
                        "<b>📬 Recipient:</b> {recipient}\n"
                        "<b>💰 Amount:</b> {amount} lamports"
}

# # Сообщения для старта и справки
# START_MESSAGES = {
#     "/start": "<b>👋 Hello, {first_name}!</b>\n\n"
#               "<i>🌕 This bot is designed to work with a wallet on the Solana blockchain.</i>\n"
#               "<i>💳 Here you can buy, sell, store, and pay using your wallet.</i>\n"
#               "<i>🤖 The bot is currently using the Solana development network API:</i>\n"
#               "<i>https://api.testnet.solana.com</i>"
#               "\n\n❓ To view the list of available commands, type /help 😊",
# }

START_MESSAGES = {
    "/start": "<b>👋 Hello, {first_name}!</b>\n\n"
              "<i>This bot is designed to work with a wallet on the Solana blockchain.</i>\n"
              "<i>Here you can buy, sell, store, and pay using your wallet.</i>\n"
              "\n\nTo view the list of available commands, type /help 😊"
              "<i>🌕 This bot is designed to work with a wallet on the Solana blockchain.</i>\n"
              "<i>💳 Here you can buy, sell, store, and pay using your wallet.</i>\n"
              "<i>🤖 The bot is currently using the Solana development network API:</i>\n"
            #   "<i>https://api.devnet.solana.com</i>"
              "<i>https://api.testnet.solana.com</i>"
              "\n\n❓ To view the list of available commands, type /help 😊",
}


# Справочное сообщение бота
HELP_MESSAGES = {
    "/help": "<b>Available commands:</b>\n\n"
             "💰 <b>balance</b> - show balance...\n\n"
             "📜 <b>transactions</b> - view transaction history...\n\n"
             "💸 <b>send</b> - send coins...\n\n"
             "📥 <b>receive</b> - receive coins...\n\n"
             "🗑️ <b>delete_wallet</b> - delete wallet...\n"
}
UNKNOWN_MESSAGE = {
    "unexpected_message": "<b>❓ Unknown command or message.</b>\n\n"
                          "Please use one of the available commands\n"
                          "or options from the menu."
}

# Объединение всех сообщений в словарь LEXICON
LEXICON: dict[str, str] = {**GENERAL_MESSAGE, **CREATE_WALLET_MESSAGE, **OTHER_BUTTONS, **CONNECT_WALLET_MESSAGE,
                           **BALANCE_MESSAGE, **TOKEN_PRICE_MESSAGE, **TOKEN_BUY_MESSAGE, **TOKEN_SELL_MESSAGES,
                           **MAIN_MENU_BUTTONS, **TOKEN_TRANSFER_TRANSACTION_MESSAGE, **START_MESSAGES, **HELP_MESSAGES,
                           **UNKNOWN_MESSAGE}
