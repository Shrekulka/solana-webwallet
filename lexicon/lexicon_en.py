# solana_wallet_telegram_bot/pylexicon/lexicon_en.py


# Сообщения для старта и справки
START_MESSAGES = {
    "/start": "👋 <b>Hello, {first_name}!</b>\n\n"
              "💳 <i>Here you can buy, sell, store, and pay using your wallet.</i>\n\n"
              "🤖 <i>The bot is currently using the Solana development network API:</i>\n"
              "<i>{node}</i>"
              "\n\n❓ To view the list of available commands, type /help 😊",
}

# Справочное сообщение бота
HELP_MESSAGES = {
    "/help": "<b>Description of the bot functionality:</b>\n\n"
             "🔑 <b>Create wallet:</b>\n\n<i>Allows you to create a new Solana wallet."
             "After creating the wallet, you will receive a private key which you should securely store."
             "This private key is essential for any transactions or interactions with your wallet.</i>\n\n"
             "🔗<b>Connect wallet:</b>\n\n<i>Allows you to connect an existing Solana wallet to your account."
             "You will be prompted to enter the wallet address, name, and optional description.</i>\n\n"
             "💰<b>Show balance:</b>\n\n<i>Allows you to check the balance of all your connected wallets.</i>\n\n"
             "📲<b>Transfer token:</b>\n\n<i>Transfers SOL between your Solana wallets. Select a sender, enter the "
             "key, address, and amount. Once confirmed, the tokens will be transferred. Note that for a successful "
             "transfer, the sender must have a sufficient balance and be cautious when entering your private key.</i>"
             "\n\n"
             "📜 <b>View transaction history:</b>\n\n<i>Allows you to view the transaction history for one of your "
             "registered Solana wallets. After selecting the desired wallet from the list, the bot will display the "
             "history of incoming and outgoing transactions for this wallet, including details of each transaction "
             "such as the unique transaction ID, sender and recipient addresses, and the transaction amount.</i>"
}

# Кнопки главного меню
MAIN_MENU_BUTTONS: dict[str, str] = {
    "create_wallet": "🔑 Create new wallet",
    "connect_wallet": "🔗 Connect wallet",
    "balance": "💰 Show balance",
    "token_price": "💹 Show token price",
    "token_buy": "💸 Buy token",
    "token_sell": "💳 Sell tokens",
    "token_transfer": "📲 Send token",
    "transaction": "📜 View transaction history",
    "crypto_price": "💹 Price cryptocurrency",
    "delete_wallet": "🗑️ Delete wallet",
    "settings": "⚙️ Crypto wallet settings",
    "donate": "💝 Donate to the team",
}

# Дополнительные кнопки
OTHER_BUTTONS: dict[str, str] = {
    "create_wallet_constructor": "⚙️ Creating a wallet with a constructor",
    "create_wallet_from_seed": "📖 Create wallet from seed phrase",

    "connect_wallet_constructor": "⚙️ Connecting a wallet with a constructor",
    "connect_wallet_from_seed": "📖 Connecting wallet from seed phrase",
    "connect_wallet_qr": "📷 Connecting a wallet by QR code",

    "button_back": "⬅️ back",
    "save_wallet": "<i>Yes</i>",
    "cancel": "<i>No</i>",
    "return_main_keyboard": "🏠 Main menu",
}

OTHER_MESSAGES: dict[str, str] = {
    "back_to_main_menu": "<b>🏠 Main menu</b>\n\n"
                         "<i>To view the list of available commands, type /help 😊</i>",
    "create_name_wallet": "💼 <b>Please enter the name for your wallet:</b>",
    "create_description_wallet": "💬 <b>Please enter the description for your wallet:</b>",
    "invalid_wallet_name": "❌ <b>Invalid wallet name entered.</b>\n"
                           "Please enter a valid name for your wallet.",
    "invalid_wallet_description": "❌ <b>Invalid wallet description entered.</b>\n"
                                  "Please enter a valid description for your wallet.",
    "invalid_wallet_seed": "❌ <b>Invalid wallet seed entered.</b>\n"
                           "Please enter a valid seed for your wallet.",
    "this_wallet_already_exists": "⚠️ <b>This wallet address has already been connected before</b>",
    "this_wallet_name_already_exists": "⚠️ <b>This wallet name has already been used before</b>",
}

# Сообщения для создания кошелька
CREATE_WALLET_MESSAGE = {
    "choose_wallet_creation_method": "✨ <b>Please choose wallet creation method:</b>",
    "wallet_name_confirmation": "💼 <b>Your wallet name:</b> {wallet_name}",

    "wallet_description_confirmation": "💼 <b>Your wallet description:</b> {wallet_description}",
    "create_qr_wallet": "Please scan the QR code:",
    "wallet_qr_confirmation": "QR code: {qr_code}",
    "qr_code_caption": "QR code",
    "create_seed_wallet": "💼 <b>Please enter your secret seed phrase:</b>",
    "wallet_seed_confirmation": "💼 <b>Your wallet seed phrase:\n<i>{seed_phrase}</i></b>\n",
    "wallet_created_successfully": "🎉 <b><u>Wallet created successfully!</u></b>\n\n"
                                   "<b><i><u>Wallet name:</u></i>\n{name}</b>\n\n"
                                   "<b><i><u>Wallet description:</u></i>\n{description}</b>\n\n"
                                   "<b><i><u>Wallet address:</u></i>\n{wallet_address}</b>\n\n"
                                   "<b><i><u>Private key:</u></i>\n{private_key}</b>\n\n"
                                   "<b><i><u>Seed phrase:</u></i>\n{seed_phrase}</b>\n\n",

    "wallet_name_requirements": "The wallet name must consist of only letters, "
                                "numbers, spaces, hyphens and underscores.",

}

# Сообщения для 'connect_wallet'
CONNECT_WALLET_MESSAGE = {
    "choose_wallet_connection_method": "✨ <b>Please choose wallet connection method:</b>",
    "connect_wallet_add_address": "🔑 <b>Enter the wallet address to connect to the bot</b>",
    "connect_wallet_qr_scan_code": "📷 <b>Click on the QR code to scan:</b>",
    "open_camera_for_qr_scan": "Open your device's camera to scan the QR code.",

    "invalid_wallet_address": "❌ <b>Invalid wallet address!</b>",
    "wallet_connected_successfully": "🎉 <b><u>Wallet connect successfully!</u></b>\n\n"
                                   "<b><i><u>Wallet name:</u></i>\n{name}</b>\n\n"
                                   "<b><i><u>Wallet description:</u></i>\n{description}</b>\n\n"
                                   "<b><i><u>Wallet address:</u></i>\n{wallet_address}</b>\n\n",

}

# Сообщения для обработки команды balance
BALANCE_MESSAGE = {
    "no_registered_wallet": "🛑 <b>You don't have a registered wallet.</b>",
    "balance_success": "💰 <b>Your wallet balance:</b> {balance} SOL"
}

# Сообщения для переноса
TOKEN_TRANSFER_TRANSACTION_MESSAGE = {
    "transfer_recipient_address_prompt": "📬 <b>Enter the recipient's wallet address:</b>\n\n"
                                         "Note: The recipient's minimum balance\n"
                                         "should be at least 0.00089784 SOL",
    "transfer_amount_prompt": "💸 <b>Enter the amount of tokens to transfer:</b>",
    "invalid_wallet_address": "❌ <b>Invalid wallet address.</b>",
    "transfer_successful": "✅ <b>Transfer of {amount} SOL to\n\n<i>{recipient}</i>\n\nsuccessful.</b>",
    "transfer_not_successful": "❌ <b>Failed to transfer {amount} SOL to\n\n<i>{recipient}.</i></b>",
    "insufficient_balance": "❌ <b>Insufficient funds in your wallet for this transfer.</b>",
    "insufficient_balance_recipient": "❌ <b>The recipient's balance\nshould be at least 0.00089784 Sol.</b>",
    "no_wallet_connected": "🔗 <b>Please connect your wallet before transferring tokens.</b>",
    "list_sender_wallets": "📋 <b>Your wallet list:</b>\n\n<i>Click on the relevant wallet:</i>",
    "choose_sender_wallet": "🔑 <b>Enter your wallet address:</b>",
    "invalid_wallet_choice": "❌ <b>Invalid wallet choice.</b>",
    "no_wallets_connected": "❌ <b>You don't have any connected wallets.\n"
                            "<i>Connect a wallet before transferring tokens.</i></b>",
    "save_new_wallet_prompt": "💾<b>Save this wallet address:</b> ",
    "wallet_info_template": "{number}) 💼 {name} 📍 {address} 💰 {balance}",
    "invalid_amount": "❌ <b>Invalid amount.</b>",
    "transfer_sender_private_key_prompt": "<b>Enter private key or seed phrase for this wallet:</b>",
    "invalid_private_key": "❌ <b>Invalid private key.</b>",
    "invalid_seed_phrase": "❌ <b>Invalid seed phrase.</b>",
    "empty_history": "😔 Transaction history is empty.",
    "server_unavailable": "The server is currently unavailable. Please try again later.",
    "transaction_info": "💼 <b>Transaction:</b> {transaction_id}:\n"
                        "📲 <b>Sender:</b> {sender}\n"
                        "📬 <b>Recipient:</b> {recipient}\n"
                        "💰 <b>Amount:</b> {amount_in_sol} SOL"
}

# Сообщения для удаления кошелька
DELETE_WALLET_MESSAGE = {
    "button_delete_confirmation": "Delete",
    "delete_wallet_confirmation": "Delete confirmation",
    "delete_wallet_successful": "💼 Wallet \n<i>{wallet_address}</i>\n <b>successfully</b> deleted",
    "delete_wallet_not_successful": "💼 <b>Delete wallet \n<i>{wallet_address}</i>\n was <b>not successful</b></b>",
}

CRYPTO_PRICE_LEXICON: dict[str, str] = {
    "crypto_price_prompt": "<b>Enter cryptocurrency symbol\n<i>(e.g., BTC for Bitcoin) 💰:</i></b>",
    "crypto_price_result_header": "<b>Current rates for {crypto_symbol} in {currency} 📊:</b>",
    "crypto_price_result_exchange": "<b><i>{exchange_name} 🏦:</i></b>\n",
    "crypto_price_result_line": "<b>1 {crypto_symbol} = {price:.2f} {currency}</b>",
    "crypto_price_error": "❌ <b>Error retrieving cryptocurrency rates</b>",
    "no_data_available": "😔 <b>No data available</b>"
}

ERROR_LEXICON: dict[str, str] = {
    "error_message": "❌ <b>An unknown error occurred.\nPlease try again.</b>",
    "processing_error": "❌ <b>An error occurred while \nprocessing your request.\nPlease try again later.</b>",
}

# Неизвестный ввод сообщения
UNKNOWN_MESSAGE_INPUT = {
    "unexpected_message": "❓ <b>Unknown command or message.</b>\n\n"
                          "Please use one of the available commands\n"
                          "or options from the menu.",
    "unexpected_input": "❌ <b>Unexpected input</b>\n\n"
                        "Please select an action from the menu\n"
                        "or enter one of the available commands,\n"
                        "such as /start or /help.",
}

# Объединение всех сообщений в словарь LEXICON
LEXICON: dict[str, str] = {**CREATE_WALLET_MESSAGE, **OTHER_BUTTONS, **OTHER_MESSAGES, **CONNECT_WALLET_MESSAGE,
                           **HELP_MESSAGES, **BALANCE_MESSAGE, **MAIN_MENU_BUTTONS, **START_MESSAGES, **ERROR_LEXICON,
                           **UNKNOWN_MESSAGE_INPUT, **TOKEN_TRANSFER_TRANSACTION_MESSAGE, **CRYPTO_PRICE_LEXICON,
                           **DELETE_WALLET_MESSAGE}
