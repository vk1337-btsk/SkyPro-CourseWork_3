import os
from src.utils.utils import (get_list_info_from_zip, merge_and_filter_operations, check_dict_correct,
                             check_and_filter_operations, get_history_transaction_clients,
                             print_history_operations_client)
from src.constanst import BASIS_DICT_TRANSACTION, BASIS_DICT_DEPOSIT


def test_get_list_info_from_zip():
    # Тест 1. Архив есть, но в нём нет json-файлов.
    input1 = os.path.join(os.path.dirname(__file__), "data", "operations_with_not_json.zip")
    output1 = str("В файле (zip-архиве) operations_with_not_json.zip отсутствуют json-файлы. Проверьте наличие "
                  "json-файлов в архиве и попробуйте снова.")
    assert get_list_info_from_zip(input1) == output1

    # Тест 2. Архива не существует.
    input2 = os.path.join(os.path.dirname(__file__), "data", "operations_not_found.zip")
    output2 = str("Файл (zip-архив) operations_not_found.zip не найден. Проверьте наличие и/или название файла "
                  "в папке по умолчанию и попробуйте снова.")
    assert get_list_info_from_zip(input2) == output2

    # Тест 3. Архив и json-файлы есть.
    input3 = os.path.join(os.path.dirname(__file__), "data", "operations_with_2_json.zip")
    output3 = [
            [{'id': 441945886, 'state': 'EXECUTED', 'date': '2019-08-26T10:50:58.294041',
                'operationAmount': {'amount': '31957.58', 'currency': {'name': 'руб.', 'code': 'RUB'}},
                'description': 'Перевод организации', 'from': 'Maestro 1596837868705199',
                'to': 'Счет 64686473678894779589'},
                {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364',
                 'operationAmount': {'amount': '8221.37', 'currency': {'name': 'USD', 'code': 'USD'}},
                 'description': 'Перевод организации', 'from': 'MasterCard 7158300734726758',
                 'to': 'Счет 35383033474447895560'}]]
    assert get_list_info_from_zip(input3) == output3


def test_merge_and_filter_operations():
    # Тест 1. В json-файлах нет корректных операций
    input1 = [[], []]
    output1 = "В полученных json-файлах отсутствуют корректные словари с информацией об операциях."
    assert merge_and_filter_operations(input1) == output1

    # Тест 2. В json-файлах есть корректные и некорректные операции
    input2 = [
        [{'id': 441945886, 'state': 'EXECUTED', 'date': '2019-08-26T10:50:58.294041',
          'operationAmount': {'amount': '31957.58', 'currency': {'name': 'руб.', 'code': 'RUB'}},
          'description': 'Перевод организации', 'from': 'Maestro 1596837868705199',
          'to': 'Счет 64686473678894779589'}],
        [{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364',
          'operationAmount': {'amount': '8221.37', 'currency': {'name': 'USD', 'code': 'USD'}},
          'description': 'Перевод организации', 'from': 'MasterCard 7158300734726758'}]
    ]
    output2 = [{'id': 441945886, 'state': 'EXECUTED', 'date': '2019-08-26T10:50:58.294041',
                'operationAmount': {'amount': '31957.58', 'currency': {'name': 'руб.', 'code': 'RUB'}},
                'description': 'Перевод организации', 'from': 'Maestro 1596837868705199',
                'to': 'Счет 64686473678894779589'}]
    assert merge_and_filter_operations(input2) == output2


def test_check_dict_correct():
    # Тест 1. Операция проходит, т.к. идентична шаблону транзакции
    dict1 = {"id": 558167602, "state": "EXECUTED", "date": "2019-04-12T17:27:27.896421",
             "operationAmount": {"amount": "43861.89",   "currency": {"name": "USD", "code": "USD"}},
             "description": "Перевод со счета на счет", "from": "Счет 73654108430135874305",
             "to": "Счет 89685546118890842412"}
    assert check_dict_correct(dict1, BASIS_DICT_TRANSACTION, BASIS_DICT_DEPOSIT)

    # Тест 2. Операция проходит, т.к. идентична шаблону депозита
    dict2 = {"id": 558167602, "state": "EXECUTED", "date": "2019-04-12T17:27:27.896421",
             "operationAmount": {"amount": "43861.89",   "currency": {"name": "USD", "code": "USD"}},
             "description": "Перевод со счета на счет", "from": "Счет 73654108430135874305",
             "to": "Счет 89685546118890842412"}
    assert check_dict_correct(dict2, BASIS_DICT_TRANSACTION, BASIS_DICT_DEPOSIT)

    # Тест 3. Операция не проходит, т.к. не идентична шаблонам депозита или транзакции
    dict3 = {"id": 558167602, "state": "EXECUTED", "date": "2019-04-12T17:27:27.896421",
             "operationAmount": {"amount": "43861.89",   "currency": {"name": "USD", "code_____": "USD"}},
             "description": "Перевод со счета на счет", "from": "Счет 73654108430135874305",
             "to": "Счет 89685546118890842412"}
    assert not check_dict_correct(dict3, BASIS_DICT_TRANSACTION, BASIS_DICT_DEPOSIT)

    # Тест 4. Операция не проходит, т.к. значения ключей в словарях различаются
    dict3 = {"id": {558167602: 555555}, "state": "EXECUTED", "date": "2019-04-12T17:27:27.896421",
             "operationAmount": {"amount": 0, "currency": {"name": "USD", "code_____": "USD"}},
             "description": "Перевод со счета на счет", "from": "Счет 73654108430135874305",
             "to": "Счет 89685546118890842412"}
    assert not check_dict_correct(dict3, BASIS_DICT_TRANSACTION, BASIS_DICT_DEPOSIT)


def test_check_and_filter_operations():
    # Test 1. Номер карты не задан или задан неверно
    dict1 = {"id": 558167602, "state": "EXECUTED", "date": "2019-04-12T17:27:27.896421",
             "operationAmount": {"amount": "43861.89",   "currency": {"name": "USD", "code": "USD"}},
             "description": "Перевод со счета на счет", "from": "Счет 73654108430135874305",
             "to": "Счет 89685546118890842412"}
    number_card1 = ""
    assert check_and_filter_operations(dict1, number_card1)

    # Тест 2. Номер карты задан, но операция была отклонена
    dict1 = {"id": 558167602, "state": "CANCELED", "date": "2019-04-12T17:27:27.896421",
             "operationAmount": {"amount": "43861.89",   "currency": {"name": "USD", "code": "USD"}},
             "description": "Перевод со счета на счет", "from": "Счет 73654108430135874305",
             "to": "Счет 89685546118890842412"}
    number_card2 = "89685546118890842412"
    assert not check_and_filter_operations(dict1, number_card2)

    # Test 3. Номер карты задан. Это операция открытия депозита
    dict3 = {"id": 558167602, "state": "EXECUTED", "date": "2019-04-12T17:27:27.896421",
             "operationAmount": {"amount": "43861.89",   "currency": {"name": "USD", "code": "USD"}},
             "description": "Перевод со счета на счет", "to": "Счет 89685546118890842412"}
    number_card3 = "89685546118890842412"
    assert check_and_filter_operations(dict3, number_card3)

    # Test 4. Номер карты задан. Это операция транзакции
    dict4 = {"id": 558167602, "state": "EXECUTED", "date": "2019-04-12T17:27:27.896421",
             "operationAmount": {"amount": "43861.89",   "currency": {"name": "USD", "code": "USD"}},
             "description": "Перевод со счета на счет", "from": "Счет 73654108430135874305",
             "to": "Счет 89685546118890842412"}
    number_card4 = "89685546118890842412"
    assert check_and_filter_operations(dict4, number_card4)


def test_get_history_transaction_clients():
    # Тест 1. Всё хорошо, список операций фильтруется, вне зависимости от наличия номера карты
    list_operations1 = [
        {"id": 536723678, "state": "EXECUTED", "date": "2018-06-12T07:17:01.311610",
         "operationAmount": {"amount": "26334.08", "currency": {"name": "USD", "code": "USD"}},
         "description": "Перевод организации", "from": "Visa Classic 4195191172583802",
         "to": "Счет 17066032701791012883"},
        {"id": 536723678, "state": "EXECUTED", "date": "2019-06-12T07:17:01.311610",
         "operationAmount": {"amount": "26334.08", "currency": {"name": "USD", "code": "USD"}},
         "description": "Перевод организации", "from": "Visa Classic 4195191172583802",
         "to": "Счет 17066032701791012883"}]
    number_card1 = "17066032701791012883"
    answer1 = str("    \r12.06.2019 Перевод организации\n"
                  "    \rVisa Classic 4195 51** **** 3802 -> Счет **2883\n"
                  "    \r26334.08 USD\n"
                  "\n"
                  "    \r12.06.2018 Перевод организации\n"
                  "    \rVisa Classic 4195 51** **** 3802 -> Счет **2883\n"
                  "    \r26334.08 USD")

    assert get_history_transaction_clients(list_operations1, number_card1) == answer1

    # Тест 2. Подаётся пустой список
    list_operations2 = []
    number_card2 = "17066032701791012883"
    answer2 = "Данный клиент не совершал операции согласно имеющимся данным"

    assert get_history_transaction_clients(list_operations2, number_card2) == answer2


def test_print_history_operations_client():
    # Тест 1. Не удалось получить данные
    path1 = os.path.join(os.path.dirname(__file__), "data", "operations_with_not_json.zip")
    number_card1 = "90424923579946435907"
    output1 = str("В файле (zip-архиве) operations_with_not_json.zip отсутствуют json-файлы. Проверьте наличие "
                  "json-файлов в архиве и попробуйте снова.")
    assert print_history_operations_client(number_card1, path1) == output1

    # Тест 2. Не удалось получить данные, т.к. словари некорректны
    path2 = os.path.join(os.path.dirname(__file__), "data", "operations_with_incorrect_json.zip")
    number_card2 = "90424923579946435907"
    output2 = str("В полученных json-файлах отсутствуют корректные словари с информацией об операциях.")
    assert print_history_operations_client(number_card2, path2) == output2

    # Тест 3. Данные удалось получить
    path3 = os.path.join(os.path.dirname(__file__), "data", "operations_with_2_json.zip")
    number_card3 = "64686473678894779589"
    output3 = str("    \r26.08.2019 Перевод организации\n"
                  "    \rMaestro 1596 68** **** 5199 -> Счет **9589\n"
                  "    \r31957.58 руб.")
    assert print_history_operations_client(number_card3, path3) == output3
