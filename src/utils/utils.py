import json
from zipfile import ZipFile
from datetime import datetime
from src.constanst import BASIS_DICT_TRANSACTION, BASIS_DICT_DEPOSIT


def get_and_parse_json_from_zip(filename_zip: str) -> list:
    """Функция получает в аргумент название zip-архива.
    Возвращает список словарей десериализованный из json-файлов этого архива"""

    with ZipFile(filename_zip) as zip_file:
        list_files_json = [file for file in zip_file.infolist() if file.filename.rstrip(".json")]
        list_data_for_json_files = [json.load(zip_file.open(file.filename)) for file in list_files_json]
        return list_data_for_json_files


def merge_and_filter_transaction_data(data_list_json: list) -> list:
    """Функция получает список, в котором каждый элемент - список со словарями (полученными из 1 json-файла).
    Каждый словарь - информация по 1 транзакции. Функция проверяет каждый словарь на корректность шаблонному словарю
    и создаёт 2 списка операций:
     - в списке "list_correct_transaction" - корректные операции;
     - в списке "list_incorrect_transaction" - некорректные операции
     Функция возвращает список корректных операций, т.к. некорректные нам не нужны (оставил на всякий случай)"""

    list_correct_transaction = []
    list_incorrect_transaction = []

    for data_json_file in data_list_json:
        for info_transaction in data_json_file:
            if check_dict_correct(info_transaction, BASIS_DICT_TRANSACTION, BASIS_DICT_DEPOSIT):
                list_correct_transaction.append(info_transaction)
            else:
                list_incorrect_transaction.append(info_transaction)
    return list_correct_transaction


def check_dict_correct(operation_dict, transaction_temp, deposit_temp) -> bool:
    """Функция получает 2 словаря:
    - 1-й словарь "operation_dict" - словарь с информацией по операции из файла
    - 2-й словарь "transaction_temp" - словарь-шаблон транзакции
    - 3-й словарь "deposit_temp" - словарь-шаблон депозита.
    Функция сравнивает структуру и названия ключей и возвращает bool в зависимости от того
     подходит полученный словарь к одному из шаблонов"""

    is_dict = lambda dict_: isinstance(dict_, dict)

    keys1, keys2, keys3 = set(operation_dict.keys()), set(transaction_temp.keys()), set(deposit_temp.keys())
    if keys1 != keys2 and keys1 != keys3:
        return False

    for key in keys1:
        if is_dict(operation_dict[key]) and (is_dict(transaction_temp[key]) or is_dict(deposit_temp[key])):
            if not check_dict_correct(operation_dict[key], transaction_temp[key], deposit_temp[key]):
                return False
        elif not is_dict(operation_dict[key]) and not is_dict(transaction_temp[key]) or not is_dict(deposit_temp[key]):
            continue
        else:
            return False
    return True


def check_and_filter_transactions(transaction: dict, number_card_client: int) -> bool:
    """Функция принимает 2 аргумента: словарь с информацией об операции и номер карты клиента
    и возвращает True/False в зависимости от того, удовлетворяет ли эта операция запросу"""

    if transaction["state"] == "EXECUTED":
        if 'from' in transaction.keys() and 'to' not in transaction.keys():
            if number_card_client in transaction['from']:
                return True
        elif 'to' in transaction.keys() and 'from' not in transaction.keys():
            if number_card_client in transaction['to']:
                return True
        elif 'from' in transaction.keys() and 'to' in transaction.keys():
            if number_card_client in transaction['to'] or number_card_client in transaction['from']:
                return True
    return False


def get_history_transaction_clients(list_transaction: list, number_card_client: int) -> print():
    """Функция принимает 2 аргумента: список корректных транзакций и id клиента, а затем фильтрует список по:
    - принадлежности к клиенту (по id)
    - по статусу транзакции - выполненные (EXECUTED)
    Затем сортирует их по дате (от старой к новой) и возвращает список транзакций клиента"""

    list_transaction = filter(lambda transaction: check_and_filter_transactions(transaction, number_card_client),
                              list_transaction)

    list_transaction = sorted(list_transaction,
                              key=lambda d: datetime.strptime(d["date"], "%Y-%m-%dT%H:%M:%S.%f"))

    print("\n\n".join(([output_text(transaction) for transaction in list_transaction])))


def format_date(transaction: dict) -> str:
    """Функция принимает словарь с данными по транзакции и возвращает дату транзакции в соответствующем виде"""

    return datetime.strptime(transaction['date'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d.%m.%Y")


def format_payment_system_sender(transaction: dict) -> str:
    """Функция принимает словарь с данными по транзакции и возвращает информацию о платёжной системе отправителя
     в соответствующем виде"""

    return transaction['from'][:transaction['from'].find(' ')]


def format_card_number_sender(transaction: dict) -> str:
    """Функция принимает словарь с данными по транзакции и возвращает информацию о номере карты отправителя
     в соответствующем виде"""

    card_number = transaction['from'][transaction['from'].find(' ') + 1:]
    encrypted_number_card = card_number[:4] + " " + card_number[3:5] + "**" + " " + "****" + card_number[-4:]

    return encrypted_number_card


def format_card_number_recipient(transaction: dict) -> str:
    """Функция принимает словарь с данными по транзакции и возвращает информацию о номере карты получателя
     в соответствующем виде"""

    card_number = transaction['to'][transaction['to'].find(' ') + 1:]

    return str("**") + card_number[-4:]


def format_payment_system_recipient(transaction: dict) -> str:
    """Функция принимает словарь с данными по транзакции и возвращает информацию о платёжной системе получателя
     в соответствующем виде"""

    return transaction['to'][:transaction['to'].find(' ')]


def formatting_text_transaction(transaction: dict) -> str:
    """Функция принимает словарь с данными по транзакции и возвращает строку с информацией о транзакции
     в соответствующем формате"""

    # Преобразовываем информацию о транзакции в соответсвующий вид
    date = format_date(transaction)
    appointment = transaction['description']
    payment_system_sender = format_payment_system_sender(transaction)
    card_number_sender = format_card_number_sender(transaction)
    payment_system_sender_recipient = format_payment_system_recipient(transaction)
    card_number_recipient = format_card_number_recipient(transaction)
    summa_transaction = transaction['operationAmount']['amount']
    currency_transaction = transaction['operationAmount']['currency']['name']

    # Формируем текст вывода информации о транзакции
    text_transaction = f"""\
    \r{date} {appointment}
    \r{payment_system_sender} {card_number_sender} -> {payment_system_sender_recipient} {card_number_recipient}
    \r{summa_transaction} {currency_transaction}"""

    return text_transaction


def formatting_text_deposit(deposit: dict) -> str:
    """Функция принимает словарь с данными по транзакции и возвращает строку с информацией о транзакции
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
