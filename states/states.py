# solana_wallet_telegram_bot/states/states.py

from aiogram.fsm.state import StatesGroup, State


# Создаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMWallet(StatesGroup):
    """
        Class defining the finite state machine states for wallet interaction.

        Attributes:
            choose_action: State for choosing wallet action.
            add_name_wallet: State for adding wallet name.
            add_description_wallet: State for adding wallet description.
            connect_wallet_address: State for connecting wallet by address.
            connect_wallet_private_key: State for connecting wallet by private key.
            choose_sender_wallet:
            transfer_recipient_address:
            transfer_amount:
    """
    # Состояние ожидания выбора действия с кошельком

    create_wallet_add_name = State()
    create_wallet_add_description = State()

    connect_wallet_add_address = State()  # Состояние подключения кошелька по адресу
    connect_wallet_add_name = State()  # Состояние добавления имени кошелька
    connect_wallet_add_description = State()  # Состояние добавления описания кошелька

    transfer_choose_sender_wallet = State()  # Состояние выбора кошелька отправителя
    transfer_sender_private_key = State()  # Состояние ввода приватного ключа отправителя

    confirm_save_new_wallet = State()
    transfer_recipient_address = State()  # Состояние ввода адреса кошелька получателя
    transfer_amount = State()  # Состояние ввода количества токенов для передачи
    choose_transaction_wallet = State()  # Состояние выбора кошелька для транзакций
