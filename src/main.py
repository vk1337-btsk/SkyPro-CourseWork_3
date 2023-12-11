from src.utils.utils import print_history_operations_client as start_
from constanst import PATH_FOR_ZIP_FILE


if __name__ == '__main__':
    # Вводим номер карты или счёта клиент и получаем историю операций
    number_cards = input("Введите номер карты или счёта клиента для вывода истории операций: ")
    print("\n", start_(number_cards, PATH_FOR_ZIP_FILE))
