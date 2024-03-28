# solana_wallet_telegram_bot/states/states.py

from aiogram.fsm.state import StatesGroup, State


# Создаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMWallet(StatesGroup):
    """
       Класс для определения состояний Finite State Machine (FSM) для управления
       различными операциями с кошельком.
    """

    # Состояние ожидания выбора действия с кошельком
    choose_action = State()

    add_name_wallet = State()
    add_description_wallet = State()

    # Состояния ожидания ввода данных для различных операций
    enter_amount = State()  # Состояние ожидания ввода суммы
    enter_recipient_address = State()  # Состояние ожидания ввода адреса получателя
    enter_token_mint_address = State()  # Состояние ожидания ввода адреса монеты (токена)
    enter_sender_address = State()  # Состояние ожидания ввода адреса отправителя
    confirm_transaction = State()  # Состояние подтверждения транзакции
    enter_buy_amount = State()  # Состояние ожидания ввода суммы для покупки
    enter_sell_amount = State()  # Состояние ожидания ввода суммы для продажи
    upload_photo_id = State()  # Состояние ожидания загрузки фотографии удостоверения личности
    enter_password = State()  # Состояние ожидания ввода пароля
    confirm_password = State()  # Состояние подтверждения пароля
    awaiting_confirmation = State()  # Состояние ожидания подтверждения транзакции
    transaction_successful = State()  # Состояние сообщения об успешной транзакции
    transaction_failed = State()  # Состояние сообщения о неудачной транзакции
    awaiting_other_info = State()  # Состояние ожидания ввода другой дополнительной информации
    choose_token_type = State()  # Состояние выбора типа криптовалюты
    # Дополнительные состояния
    enter_email = State()  # Состояние ожидания ввода электронной почты
    enter_phone_number = State()  # Состояние ожидания ввода номера телефона
    enter_pin_code = State()  # Состояние ожидания ввода пин-кода
    enter_security_question = State()  # Состояние ожидания ввода ответа на вопрос безопасности
    confirm_transaction_details = State()  # Состояние подтверждения деталей транзакции
    awaiting_otp = State()  # Состояние ожидания ввода одноразового пароля
    enter_destination_tag = State()  # Состояние ожидания ввода тега (destination tag)
    choose_payment_method = State()  # Состояние выбора метода оплаты
    enter_card_details = State()  # Состояние ожидания ввода данных карты
    awaiting_approval = State()  # Состояние ожидания подтверждения операции
    enter_verification_code = State()  # Состояние ожидания ввода кода подтверждения
    upload_document = State()  # Состояние ожидания загрузки документов
