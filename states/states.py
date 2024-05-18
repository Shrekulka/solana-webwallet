# solana-webwallet/states/states.py

from aiogram.fsm.state import StatesGroup, State


class FSMWallet(StatesGroup):
    """
        Class of states for managing the wallet interaction process.

        Attributes:
            create_wallet_add_seed (State): State for adding the seed phrase for create a new wallet.
            create_wallet_add_name (State): State for adding the name of a new wallet.
            create_wallet_add_description (State): State for adding the description of a new wallet.
            connect_wallet_add_address (State): State for adding the address to connect an existing wallet.
            connect_wallet_add_name (State): State for adding the name of an existing wallet.
            connect_wallet_add_description (State): State for adding the description of an existing wallet.
            transfer_choose_sender_wallet (State): State for choosing the sender's wallet during token transfer.
            transfer_sender_private_key (State): State for inputting the sender's private key.
            confirm_save_new_wallet (State): State for confirming the saving of a new wallet.
            transfer_recipient_address (State): State for inputting the recipient's wallet address during token transfer
            transfer_amount (State): State for inputting the amount of tokens to transfer.
            choose_transaction_wallet (State): State for choosing the wallet to view transactions.
    """

    create_wallet_add_name = State()          # Состояние добавления имени нового кошелька
    create_wallet_add_description = State()   # Состояние добавления описания нового кошелька

    create_wallet_from_seed_add_seed = State()          # Состояние добавления seed фразы для нового кошелька
    create_wallet_from_seed_add_name = State()
    create_wallet_from_seed_add_description = State()

    connect_wallet_add_address = State()      # Состояние добавления адреса для подключения существующего кошелька
    connect_wallet_add_name = State()         # Состояние добавления имени существующего кошелька
    connect_wallet_add_description = State()  # Состояние добавления описания существующего кошелька

    transfer_choose_sender_wallet = State()   # Состояние выбора кошелька отправителя при переводе токенов
    transfer_sender_private_key = State()     # Состояние ввода приватного ключа отправителя

    confirm_save_new_wallet = State()         # Состояние подтверждения сохранения нового кошелька
    transfer_recipient_address = State()      # Состояние ввода адреса кошелька получателя при переводе токенов
    transfer_amount = State()                 # Состояние ввода количества токенов для передачи
    choose_transaction_wallet = State()       # Состояние выбора кошелька для просмотра транзакций

    delete_wallet = State()
