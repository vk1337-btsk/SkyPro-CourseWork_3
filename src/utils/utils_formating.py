from datetime import datetime
from src.constanst import BASIS_DICT_TRANSACTION, BASIS_DICT_DEPOSIT


def format_date(operation: dict) -> str:
    """Функция принимает словарь с данными по операции и возвращает дату операции в соответствующем виде"""

    return datetime.strptime(operation['date'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d.%m.%Y")


def format_payment_system_sender(operation: dict) -> str:
    """Функция принимает словарь с данными по операции и возвращает информацию о платёжной системе отправителя
     в соответствующем виде"""

    return operation['from'][:operation['from'].rfind(' ')]


def format_card_number_sender(operation: dict) -> str:
    """Функция принимает словарь с данными по операции и возвращает информацию о номере карты отправителя
     в соответствующем виде"""

    card_number = operation['from'][operation['from'].rfind(' ') + 1:]
    encrypted_number_card = card_number[:4] + " " + card_number[3:5] + "**" + " " + "****" + " " + card_number[-4:]

    return encrypted_number_card


def format_card_number_recipient(operation: dict) -> str:
    """Функция принимает словарь с данными по операции и возвращает информацию о номере карты получателя
     в соответствующем виде"""

    card_number = operation['to'][operation['to'].rfind(' ') + 1:]

    return str("**") + card_number[-4:]


def format_payment_system_recipient(operation: dict) -> str:
    """Функция принимает словарь с данными по операции и возвращает информацию о платёжной системе получателя
     в соответствующем виде"""

    return operation['to'][:operation['to'].rfind(' ')]


def formatting_text_transaction(operation: dict) -> str:
    """Функция принимает словарь с данными по транзакции и возвращает строку с информацией о транзакции
     в соответствующем формате"""

    # Преобразовываем информацию об операции в соответсвующий вид
    date = format_date(operation)
    appointment = operation['description']
    payment_system_sender = format_payment_system_sender(operation)
    card_number_sender = format_card_number_sender(operation)
    payment_system_sender_recipient = format_payment_system_recipient(operation)
    card_number_recipient = format_card_number_recipient(operation)
    summa_transaction = operation['operationAmount']['amount']
    currency_transaction = operation['operationAmount']['currency']['name']

    # Формируем текст вывода информации об операции
    text_transaction = f"""\
    \r{date} {appointment}
    \r{payment_system_sender} {card_number_sender} -> {payment_system_sender_recipient} {card_number_recipient}
    \r{summa_transaction} {currency_transaction}"""

    return text_transaction


def formatting_text_deposit(deposit: dict) -> str:
    """Функция принимает словарь с данными по операции и возвращает строку с информацией об операции
     в соответствующем формате"""

    # Преобразовываем информацию о транзакции в соответсвующий вид
    date = format_date(deposit)
    appointment = deposit['description']
    payment_system = format_payment_system_recipient(deposit)
    card_number = format_card_number_recipient(deposit)
    summa_deposit = deposit['operationAmount']['amount']
    currency_deposit = deposit['operationAmount']['currency']['name']

    # Формируем текст вывода информации о транзакции
    text_transaction = f"""\
    \r{date} {appointment}
    \r{payment_system} {card_number}
    \r{summa_deposit} {currency_deposit}"""

    return text_transaction


def output_text(transaction: dict) -> str:
    """Функция принимает словарь с данными по транзакции и в зависимости от операции выводит
    соответствующий текст с информацией"""

    if transaction.keys() == BASIS_DICT_TRANSACTION.keys():
        return formatting_text_transaction(transaction)
    elif transaction.keys() == BASIS_DICT_DEPOSIT.keys():
        return formatting_text_deposit(transaction)
