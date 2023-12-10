from utils.utils import get_and_parse_json_from_zip, merge_and_filter_transaction_data, get_history_transaction_clients
from src.constanst import ROOT_DIR, NAME_ZIP_FILE
import os


if __name__ == '__main__':

    # Получаем информацию о транзакциях из json-файлов в архиве
    data_transactions = get_and_parse_json_from_zip(os.path.join(ROOT_DIR, "data", NAME_ZIP_FILE))

    # Объединяем и фильтруем корректные транзакции
    list_transactions = merge_and_filter_transaction_data(data_transactions)

    # Вводим номер карты или счёта клиент
    number_cards = int(input("Введите номер карты или счёта клиента для вывода истории операций: "))

    # Получаем id-клиента и печатаем последние 5 операций клиента
    get_history_transaction_clients(list_transactions, number_cards)