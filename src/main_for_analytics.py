from utils.utils_analytics import list_command, get_history_operations
from constanst import PATH_FOR_ZIP_FILE


# Получаем список банковских операций или информационное сообщение, если на каком-то этапе произошла ошибка
list_operations = get_history_operations(PATH_FOR_ZIP_FILE)


if __name__ == '__main__':
    # Приветствие с юзером
    print('Здравствуй, аналитик. Я специальное ПО, позволяющее анализировать банковские операции.\n'
          'Для того, чтобы получить какую-либо аналитику по банковским операциям впишите нужную команду.\n'
          'Если вы не знакомы с командами и моими возможностями, то введите "help".'
          'Чтобы выйти введите exit.\n\n'
          'Давайте начнём. Сейчас загружу данные...')

    # Проверка на то, получены данные или нет
    if isinstance(list_operations, str):
        print(list_operations)
    else:
        command_user = input("Введите команду: ").lower()

        while command_user != "exit":
            print(list_command(list_operations, command_user))
            command_user = input("Введите команду: ").lower()

    print('\nДо встречи!\nThe end...')
