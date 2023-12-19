from src.utils.utils import get_list_info_from_zip, merge_and_filter_operations
from datetime import datetime


def list_command(list_operations: list, command: str) -> str:
    """В функцию подаётся два аргумента: список с информацией об операции и команда. Функция возвращает
    либо информационное сообщение, если на каком-то этапе возникла ошибка, либо результат этой команды"""

    list_commands = {'help': [None, "Распечатать все команды и их функционал."],
                     "total": [info_operations_amount(list_operations), "Вывести сумму всех операций."],
                     "max": [info_max_amount(list_operations), "Вывести наибольшую сумму операции."],
                     "min": [info_min_amount(list_operations), "Вывести наименьшую сумму операции."],
                     "account_max_count_operation":
                         [info_max_count_operations(list_operations), "Вывести счёт с наибольшим количеством "
                                                                      "операций."],
                     "count_unique_account":
                         [info_count_unique_bank_account(list_operations), "Вывести количество уникальных счетов, "
                                                                           "которые осуществляли операции."]
                     }
    if command.strip() != 'help':
        if command in list_commands.keys():
            text_message = str(f"\nВы ввели команду '{command}'. Выводим "
                               f"{str(list_commands[command][1])[list_commands[command][1].find(' ')+1:]}\n")
            text_report = list_commands.get(command)[0]
            text = f'{text_message}{text_report}'
            return text
        else:
            return f"Команды {command} в моём арсенале нет. Введите 'help' для помощи или 'exit' для выхода."
    else:
        text = "В моём распоряжении имеются следующие команды: \n"
        for commands, inf_commands in list_commands.items():
            text += f"'{commands}' - {inf_commands[1]}\n"
        return text


def get_history_operations(path_for_zip_file: str) -> str or list:
    """Функция принимает аргументом абсолютный путь до файла с историей операций. Функция возвращает либо
    информационное сообщение, если на каком-то этапе получение информации не удалось, либо список этих операций."""

    # Получаем информацию о транзакциях из json-файлов в архиве
    data_transactions = get_list_info_from_zip(path_for_zip_file)

    # Проверяем является ли data_transactions - строкой, если да, то возвращаем информационное сообщение
    if isinstance(data_transactions, str):
        return data_transactions

    else:
        # Объединяем и фильтруем корректные транзакции
        list_transactions = merge_and_filter_operations(data_transactions)
        # Проверяем является ли list_transactions - строкой, если да, то возвращаем информационное сообщение
        if isinstance(list_transactions, str):
            return list_transactions

        # Если всё хорошо, то возвращаем список с операциями
        return list_transactions


def info_operations_amount(list_operations: list) -> str:
    """Функция получает список операций со словарями об операции внутри и возвращает словарь в формате:
        {'deposit': {'RUB': 0.0, 'USD': 0.0}, 'transaction': {'RUB': 0.0, 'USD': 0.0}}
    Где указана сумма всех транзакция и открытий вкладов в разрезе валют"""

    summa_operations = {'deposit': {'RUB': 0.0, 'USD': 0.0}, 'transaction': {'RUB': 0.0, 'USD': 0.0}}

    for operation in list_operations:
        if operation['description'] == "Открытие вклада" and operation['state'] == 'EXECUTED':
            code_currency = operation['operationAmount']['currency']['code']
            summa_operations['deposit'][code_currency] += float(operation['operationAmount']['amount'])

        else:
            code_currency = operation['operationAmount']['currency']['code']
            summa_operations['transaction'][code_currency] += float(operation['operationAmount']['amount'])

    summa_operations = {key: {k: round(v, 2) for k, v in value.items()} for key, value in summa_operations.items()}

    dict_names_operation = {'deposit': "Открыто вкладов за отчётный период:\n",
                            'transaction': "Совершено транзакций за отчётный период:\n"}
    dict_currency = {"RUB": "\t- в рублях: ", "USD": "\t- в долларах: "}

    text = ""

    for operation, dict_currencies in summa_operations.items():
        text += str(dict_names_operation.get(operation))
        for currency, total in dict_currencies.items():
            text += dict_currency[currency] + f"{total:,.2f}" + "\n"

    return text


def info_max_amount(list_operations: list) -> str:
    text = ""

    # Блок для формирования текста по транзакциям
    for currency in ("RUB", "USD"):
        max_summa = max(filter(lambda operation: operation['state'] == 'EXECUTED' and "from" in operation.keys()
                               and operation['operationAmount']['currency']['code'] == currency, list_operations),
                        key=lambda operation: float(operation['operationAmount']['amount']))
        text_currency = 'рублях' if currency == 'RUB' else 'долларах'
        text_date = datetime.strptime(max_summa['date'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d.%m.%Y")
        text_card_sender = max_summa['from']
        text_card_recipient = max_summa['to']
        text_description = max_summa['description']
        text_summa = max_summa['operationAmount']['amount']
        text_max_tr = (f"Максимальная сумма транзакции в {text_currency}:\n"
                       f"{text_date}: {text_card_sender} -> {text_card_recipient}. Назначение: "
                       f"{text_description.lower()}\n"
                       f"{text_summa} {currency}\n")
        text += text_max_tr

    # Блок для формирования текста по депозиту
    for currency in ("RUB", "USD"):
        max_summa = max(filter(lambda operation: operation['state'] == 'EXECUTED' and "from" not in operation.keys()
                               and operation['operationAmount']['currency']['code'] == currency, list_operations),
                        key=lambda operation: float(operation['operationAmount']['amount']))
        text_currency = 'рублях' if currency == 'RUB' else 'долларах'
        text_date = datetime.strptime(max_summa['date'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d.%m.%Y")
        text_card_recipient = max_summa['to']
        text_description = max_summa['description']
        text_summa = max_summa['operationAmount']['amount']
        text_max_tr = (f"Максимальная сумма депозита в {text_currency}:\n"
                       f"{text_date}: -> {text_card_recipient}. Назначение: {text_description.lower()}\n"
                       f"{text_summa} {currency}\n")
        text += text_max_tr

    return text


def info_min_amount(list_operations: list) -> str:
    text = ""

    # Блок для формирования текста по транзакциям
    for currency in ("RUB", "USD"):
        min_summa = min(filter(lambda operation: operation['state'] == 'EXECUTED' and "from" in operation.keys()
                               and operation['operationAmount']['currency']['code'] == currency, list_operations),
                        key=lambda operation: float(operation['operationAmount']['amount']))
        text_currency = 'рублях' if currency == 'RUB' else 'долларах'
        text_date = datetime.strptime(min_summa['date'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d.%m.%Y")
        text_card_sender = min_summa['from']
        text_card_recipient = min_summa['to']
        text_description = min_summa['description']
        text_summa = min_summa['operationAmount']['amount']
        text_max_tr = (f"Минимальная сумма транзакции в {text_currency}:\n"
                       f"{text_date}: {text_card_sender} -> {text_card_recipient}. "
                       f"Назначение: {text_description.lower()}\n"
                       f"{text_summa} {currency}\n")
        text += text_max_tr

    # Блок для формирования текста по депозиту
    for currency in ("RUB", "USD"):
        min_summa = min(filter(lambda operation: operation['state'] == 'EXECUTED' and "from" not in operation.keys()
                               and operation['operationAmount']['currency']['code'] == currency, list_operations),
                        key=lambda operation: float(operation['operationAmount']['amount']))
        text_currency = 'рублях' if currency == 'RUB' else 'долларах'
        text_date = datetime.strptime(min_summa['date'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d.%m.%Y")
        text_card_recipient = min_summa['to']
        text_description = min_summa['description']
        text_summa = min_summa['operationAmount']['amount']
        text_max_tr = (f"Минимальная сумма депозита в {text_currency}:\n"
                       f"{text_date}: -> {text_card_recipient}. Назначение: {text_description.lower()}\n"
                       f"{text_summa} {currency}\n")
        text += text_max_tr

    return text


def info_max_count_operations(list_operations: list) -> str:
    dict_accounts = {}
    for operation in list_operations:
        if operation['state'] == 'EXECUTED':
            for value in ['from', 'to']:
                if 'from' not in operation.keys():
                    continue
                else:
                    number_account = operation[value][operation[value].rfind(' ')+1:]
                    if number_account in dict_accounts.keys():
                        dict_accounts[number_account].append(operation)
                    else:
                        dict_accounts[number_account] = [operation]
    account = max(dict_accounts.items(), key=lambda account_: len(account_[1]))
    if len(account[1]) == 1:
        text = (f"Клиента с наибольшим количеством операций не существует. "
                f"Максимальное количество операций у одного клиента - 1.")
        return text
    else:
        text = f"Счёт № {account[0]} с количеством операций - {len(account[1])}."
    return text


def info_count_unique_bank_account(list_operations: list) -> str:
    dict_accounts = {}
    for operation in list_operations:
        if operation['state'] == 'EXECUTED':
            for value in ['from', 'to']:
                try:
                    number_account = operation[value][operation[value].rfind(' ') + 1:]
                    if number_account in dict_accounts.keys():
                        dict_accounts[number_account].append(operation)
                    else:
                        dict_accounts[number_account] = [operation]
                except KeyError:
                    pass
    if len(dict_accounts) == 0:
        text = f'Информация об операциях отсутствует...'
    else:
        text = f'Всего уникальных клиентов, участвовавших в операциях - {len(dict_accounts)}'
    return text
