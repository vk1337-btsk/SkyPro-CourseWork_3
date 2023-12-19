import pytest
from src.utils.utils_formating import (format_date, format_payment_system_sender, format_card_number_sender,
                                       format_card_number_recipient, format_payment_system_recipient,
                                       formatting_text_transaction, formatting_text_deposit, output_text)


@pytest.fixture
def info_transactions():
    transaction = {"id": 441945886, "state": "EXECUTED", "date": "2019-08-26T10:50:58.294041",
                   "operationAmount": {"amount": "31957.58", "currency": {"name": "руб.", "code": "RUB"}},
                   "description": "Перевод организации", "from": "Maestro 1596837868705199",
                   "to": "Счет 64686473678894779589"}
    return transaction


@pytest.fixture
def info_deposit():
    deposit = {"id": 596171168, "state": "EXECUTED", "date": "2018-07-11T02:26:18.671407",
               "operationAmount": {"amount": "79931.03", "currency": {"name": "руб.", "code": "RUB"}},
               "description": "Открытие вклада", "to": "Счет 72082042523231456215"}
    return deposit


def test_format_date(info_transactions):
    assert format_date(info_transactions) == "26.08.2019"


def test_format_payment_system_sender(info_transactions):
    assert format_payment_system_sender(info_transactions) == "Maestro"


def test_format_card_number_sender(info_transactions):
    assert format_card_number_sender(info_transactions) == "1596 68** **** 5199"


def test_format_card_number_recipient(info_transactions):
    assert format_card_number_recipient(info_transactions) == "**9589"


def test_format_payment_system_recipient(info_transactions):
    assert format_payment_system_recipient(info_transactions) == "Счет"


def test_formatting_text_transaction(info_transactions):
    text = str("    \r26.08.2019 Перевод организации\n"
               "    \rMaestro 1596 68** **** 5199 -> Счет **9589\n"
               "    \r31957.58 руб.")
    assert formatting_text_transaction(info_transactions) == text


def test_formatting_text_deposit(info_deposit):
    text = str("    \r11.07.2018 Открытие вклада\n"
               "    \rСчет **6215\n"
               "    \r79931.03 руб.")
    assert formatting_text_deposit(info_deposit) == text


def test_output_text(info_deposit, info_transactions):
    text_deposit = str("    \r11.07.2018 Открытие вклада\n"
                       "    \rСчет **6215\n"
                       "    \r79931.03 руб.")
    assert output_text(info_deposit) == text_deposit

    text_transaction = str("    \r26.08.2019 Перевод организации\n"
                           "    \rMaestro 1596 68** **** 5199 -> Счет **9589\n"
                           "    \r31957.58 руб.")
    assert output_text(info_transactions) == text_transaction
