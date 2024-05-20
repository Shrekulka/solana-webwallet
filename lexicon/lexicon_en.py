# solana_wallet_telegram_bot/pylexicon/lexicon_en.py


# Сообщения для старта и справки
START_MESSAGES = {
    "/start": "<b>👋 Hello, {first_name}!</b>\n\n"
              "<i>💳 Here you can buy, sell, store, and pay using your wallet.</i>\n\n"
              "<i>🤖 The bot is currently using the Solana development network API:</i>\n"
              "<i>{node}</i>"
              "\n\n❓ To view the list of available commands, type /help 😊",
}

# Справочное сообщение бота
HELP_MESSAGES = {
    "/help": "<b>Description of the bot functionality:</b>\n\n"
             "🔑 <b>Create wallet:</b>\n\n<i>Allows you to create a new Solana wallet."
             "After creating the wallet, you will receive a private key which you should securely store."
             "This private key is essential for any transactions or interactions with your wallet.</i>\n\n"
             "🔗<b> Connect wallet:</b>\n\n<i>Allows you to connect an existing Solana wallet to your account."
             "You will be prompted to enter the wallet address, name, and optional description.</i>\n\n"
             "💰<b> Show balance:</b>\n\n<i>Allows you to check the balance of all your connected wallets.</i>\n\n"
             "📲<b> Transfer token:</b>\n\n<i>Transfers SOL between your Solana wallets. Select a sender, enter the "
             "key, address, and amount. Once confirmed, the tokens will be transferred. Note that for a successful "
             "transfer, the sender must have a sufficient balance and be cautious when entering your private key.</i>"
             "\n\n"
             "<b>📜 View transaction history:</b>\n\n<i>Allows you to view the transaction history for one of your "
             "registered Solana wallets. After selecting the desired wallet from the list, the bot will display the "
             "history of incoming and outgoing transactions for this wallet, including details of each transaction "
             "such as the unique transaction ID, sender and recipient addresses, and the transaction amount.</i>"
}

# Кнопки главного меню
MAIN_MENU_BUTTONS: dict[str, str] = {
    "create_wallet": "🔑 Create wallet",
    "connect_wallet": "🔗 Connect wallet",
    "balance": "💰 Show balance",
    "token_price": "💹 Show token price",
    "token_buy": "💸 Buy token",
    "token_sell": "💳 Sell tokens",
    "token_transfer": "📲 Send token",
    "transaction": "📜 View transaction history",
    "delete_wallet": "🗑️ Delete wallet",
    "settings": "⚙️ Crypto wallet settings",
    "donate": "💝 Donate to the team",
}

# Дополнительные кнопки
OTHER_BUTTONS: dict[str, str] = {
    "button_back": "⬅️ back",
    "back_to_main_menu": "<b>🏠 Main menu</b>\n\n"
                         "<i>To view the list of available commands, type /help 😊</i>",
    "save_wallet": "<i>Yes</i>",
    "cancel": "<i>No</i>",
}

# Сообщения для создания кошелька
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

# Сообщения для переноса
TOKEN_TRANSFER_TRANSACTION_MESSAGE = {
    "transfer_recipient_address_prompt": "<b>📬 Enter the recipient's wallet address:</b>\n\n"
                                         "Note: The recipient's minimum balance\n"
                                         "should be at least 0.00089784 SOL",
    "transfer_amount_prompt": "<b>💸 Enter the amount of tokens to transfer:</b>",
    "invalid_wallet_address": "<b>❌ Invalid wallet address.</b>",
    "transfer_successful": "<b>✅ Transfer of {amount} SOL to\n\n<i>{recipient}</i>\n\nsuccessful.</b>",
    "transfer_not_successful": "<b>❌ Failed to transfer {amount} SOL to\n\n<i>{recipient}.</i></b>",
    "insufficient_balance": "<b>❌ Insufficient funds in your wallet for this transfer.</b>",
    "insufficient_balance_recipient": "<b>❌ The recipient's balance\nshould be at least 0.00089784 Sol.</b>",
    "no_wallet_connected": "<b>🔗 Please connect your wallet before transferring tokens.</b>",
    "list_sender_wallets": "<b>📋 Your wallet list:</b>\n\n<i>Click on the relevant wallet:</i>",
    "choose_sender_wallet": "<b>🔑 Enter your wallet address:</b>",
    "invalid_wallet_choice": "<b>❌ Invalid wallet choice.</b>",
    "no_wallets_connected": "<b>❌ You don't have any connected wallets.\n"
                            "<i>Connect a wallet before transferring tokens.</i></b>",
    "save_new_wallet_prompt": "<b>💾 Save this wallet address:</b> ",
    "wallet_info_template": "{number}) 💼 {name} 📍 {address} 💰 {balance}",
    "invalid_amount": "<b>❌ Invalid amount.</b>",
    "transfer_sender_private_key_prompt": "<b>Enter private key for this wallet:</b>",
    "invalid_private_key": "<b>❌ Invalid private key.</b>",
    "empty_history": "😔 Transaction history is empty.",
    "server_unavailable": "The server is currently unavailable. Please try again later.",
    "transaction_info": "<b>💼 Transaction:</b> {transaction_id}:\n"
                        "<b>📲 Sender:</b> {sender}\n"
                        "<b>📬 Recipient:</b> {recipient}\n"
                        "<b>💰 Amount:</b> {amount_in_sol} SOL"
}

# Неизвестный ввод сообщения
UNKNOWN_MESSAGE_INPUT = {
    "unexpected_message": "<b>❓ Unknown command or message.</b>\n\n"
                          "Please use one of the available commands\n"
                          "or options from the menu.",
    "unexpected_input": "❌ <b>Unexpected input</b>\n\n"
                        "Please select an action from the menu\n"
                        "or enter one of the available commands,\n"
                        "such as /start or /help.",
}

# Объединение всех сообщений в словарь LEXICON
LEXICON: dict[str, str] = {**CREATE_WALLET_MESSAGE, **OTHER_BUTTONS, **CONNECT_WALLET_MESSAGE, **HELP_MESSAGES,
                           **BALANCE_MESSAGE, **MAIN_MENU_BUTTONS, **START_MESSAGES, **UNKNOWN_MESSAGE_INPUT,
                           **TOKEN_TRANSFER_TRANSACTION_MESSAGE}
