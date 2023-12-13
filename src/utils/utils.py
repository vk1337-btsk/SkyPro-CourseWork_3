import json
from zipfile import ZipFile
from datetime import datetime
from src.constanst import BASIS_DICT_TRANSACTION, BASIS_DICT_DEPOSIT
from src.utils.utils_formating import output_text


def get_list_info_from_zip(filename_zip: str) -> list or str:
    """Функция получает в аргумент полный путь до zip-архива. Возвращает десериализованный из json-файлов этого архива
    список списков словарей (где каждый список - это словари с информацией об операциях из одного json-файла,
    а словарь - информация об одной операции).
    В случае отсутствия zip-архива в папке возвращает сообщение:
    'Файл (zip-архив) <название zip-архива> не найден. Проверьте наличие и/или название файла в папке по умолчанию
    и попробуйте снова.'
    В случае отсутствия json-файлов в zip-архиве возвращает сообщение:
    'В файле (zip-архиве) <название zip-архива> отсутствуют json-файлы. Проверьте наличие json-файлов в архиве
    и попробуйте снова.'"""

    # Получаем название zip-архива
    name_file = filename_zip[filename_zip.rfind('\\') + 1:]

    try:
        with ZipFile(filename_zip) as zip_file:
            # Проходим по файлам zip-архива, в случае, если это json, то добавляем его в список файлов для обработки
            list_files_json = [file for file in zip_file.infolist() if file.filename.rstrip(".json")]

            # Если в zip-архиве не найдено json-файлов, то возвращаем информационное сообщение
            if len(list_files_json) == 0:
                return (f"В файле (zip-архиве) {name_file} отсутствуют json-файлы. Проверьте наличие "
                        f"json-файлов в архиве и попробуйте снова.")

            else:
                # Если json-файлы найдены, то проходим по ним и десериализируем их и добавляем в список
                list_data_for_json_files = [json.load(zip_file.open(file.filename)) for file in list_files_json]
                return list_data_for_json_files

    except FileNotFoundError:
        # Если zip-архив не найден, то возвращаем информационное сообщение
        return (f"Файл (zip-архив) {name_file} не найден. Проверьте наличие и/или название файла "
                f"в папке по умолчанию и попробуйте снова.")


def merge_and_filter_operations(data_list_json: list) -> list or str:
    """Функция получает список, в котором каждый элемент - список со словарями (полученными из одного json-файла).
    Каждый словарь - информация по одной транзакции. Функция проверяет каждый словарь на корректность шаблонному словарю
    и создаёт 2 списка с информацией об операциях:
     - в списке "list_correct_operations" - корректные операции;
     - в списке "list_incorrect_operations" - некорректные операции
     Функция возвращает список корректных операций, т.к. возврате некорректных нет необходимости"""

    # Создаём список для корректных и некорректных операциях
    list_correct_operations = []
    list_incorrect_operations = []

    # Проходим по циклу, где каждый элемент - список со словарями (каждый словарь - информация об операции)
    for data_json_file in data_list_json:
        for info_operation in data_json_file:

            # Проверяем словарь с информацией об операции на идентичность базовому словарю с информацией об операции
            if check_dict_correct(info_operation, BASIS_DICT_TRANSACTION, BASIS_DICT_DEPOSIT):
                # Словарь корректен -> добавляем в список для корректных операций
                list_correct_operations.append(info_operation)
            else:
                # Словарь некорректен -> добавляем в список для некорректных операций
                list_incorrect_operations.append(info_operation)

    # Проверяем, есть ли в словаре хотя бы одна операция, если нет, то возвращаем информационно сообщение
    if not list_correct_operations:
        return 'В полученных json-файлах отсутствуют корректные словари с информацией об операциях.'
    else:
        return list_correct_operations


def check_dict_correct(info_operation, transaction_temp=None, deposit_temp=None) -> bool:
    """Функция принимает в аргументы три словаря:
    - 1-й словарь "operation_dict" - словарь с информацией по операции из файла
    - 2-й словарь "transaction_temp" - словарь-шаблон с информацией по транзакции
    - 3-й словарь "deposit_temp" - словарь-шаблон с информацией по открытию депозита.
    Функция сравнивает структуру и названия ключей и возвращает bool в зависимости от того
    подходит полученный словарь к одному из шаблонов или нет"""

    # Создаём переменные со списком ключей (нужно для визуального уменьшения кода и простоты чтения)
    keys1, keys2, keys3 = info_operation.keys(), transaction_temp.keys(), deposit_temp.keys()
    # Проверяем идентичен ли полученный список ключей из операции шаблонам
    if keys1 != keys2 and keys1 != keys3:
        return False

    # Если список ключей идентичен какому-либо шаблону, то проходим по парам ключ-значение
    # и проверяем являются ли значения словарями для проверки внутри этих словарей
    for key in keys1:
        # Если значение нашего ключа и ключа из шаблона - словарь, то проваливаемся внутрь
        # и проверяем этот словарь на предмет идентичности
        if isinstance(info_operation[key], dict) and (isinstance(transaction_temp[key], dict)
                                                      or isinstance(deposit_temp[key], dict)):
            if not check_dict_correct(info_operation[key], transaction_temp[key], deposit_temp[key]):
                return False
        # Если значение нашего ключа и ключа из шаблона - не словарь и имеет один тип данных, то идём дальше по ключам
        elif (not isinstance(info_operation[key], dict) and not isinstance(transaction_temp[key], dict)
              or not isinstance(deposit_temp[key], dict)
              and type(info_operation[key]) is (type(transaction_temp[key]) or type(deposit_temp[key]))):
            continue
        # Если значение нашего ключа - один тип данных, а значение ключа из шаблона - другой тип данных,
        # то возвращаем False
        else:
            return False
    # Если дошли до этого этапа, то проверка пройдена, возвращаем True
    return True


def check_and_filter_operations(operation: dict, number_card_client: str) -> bool:
    """Функция принимает два аргумента: словарь с информацией об операции и номер карты клиента
    и возвращает True/False в зависимости от того присутствует ли в этой операции карта клиента
    (как отправителя или как получателя), а также по фактору того, что операция была выполнена"""

    if number_card_client != "" and number_card_client.isdigit():
        # Проверка на то, выполнена ли была операция
        if operation["state"] == "EXECUTED":
            # Если операция выполнена и это открытие вклада
            if 'to' in operation.keys() and 'from' not in operation.keys():
                if number_card_client in operation['to']:
                    return True
            # Если операция выполнена и это открытие транзакция
            elif 'from' in operation.keys() and 'to' in operation.keys():
                if number_card_client in operation['to'] or number_card_client in operation['from']:
                    return True
        # Если операция была не выполнена и/или операция не имеет отношения к клиенту, то возвращаем False
        else:
            return False
    else:
        return True


def get_history_transaction_clients(list_transaction: list, number_card_client: str) -> str:
    """Функция принимает 2 аргумента: список корректных транзакций и id клиента, а затем фильтрует список по:
    - принадлежности к клиенту (по id)
    - по статусу транзакции - выполненные (EXECUTED)
    Затем сортирует их по дате (от старой к новой) и возвращает список транзакций клиента.
    Если номер карты не передан, то возвращается 5 последних операций.
    В случае того, что операции не найдены (или не подходят по условию, то выводим информационное сообщение)"""

    if number_card_client != "" and number_card_client.isdigit():
        # Проходим по имеющимся операциям и отфильтровываем те, что не относятся к операции клиента или к выполненным
        list_transaction = list(filter(lambda transaction: check_and_filter_operations(transaction, number_card_client),
                                list_transaction))

    list_transaction = sorted(list_transaction,
                              key=lambda d: datetime.strptime(d["date"], "%Y-%m-%dT%H:%M:%S.%f"), reverse=True)

    # Если список операций пуст, то выводим информационное сообщение, о том
    if not list_transaction:
        return "Данный клиент не совершал операции согласно имеющимся данным"

    text = "\n\n".join(([output_text(transaction) for transaction in list_transaction][:5]))
    return text


def print_history_operations_client(number: str, path_for_zip_file: str) -> str:
    """Функция принимает аргументом номер карты клиента и абсолютный путь до файла с историей операций
     и осуществляет поиск операций в которых участвовал клиент, по имеющимся json-файлам. Функция возвращает
     либо информационное сообщение, если на каком-то этапе поиск не удался, либо список этих операций"""

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

        else:
            # Осуществляем поиск последние 5 операций клиента
            return get_history_transaction_clients(list_transactions, number)
