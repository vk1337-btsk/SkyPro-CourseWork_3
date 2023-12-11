import os


ROOT_DIR = os.path.dirname(__file__)

NAME_ZIP_FILE = "operations.zip"

PATH_FOR_ZIP_FILE = os.path.join(ROOT_DIR, "data", NAME_ZIP_FILE)

BASIS_DICT_TRANSACTION = {'id': 0, 'state': 0, 'date': 0,
                          'operationAmount': {'amount': 0, 'currency': {'name': 0, 'code': 0}},
                          'description': 0, 'from': 0, 'to': 0}

BASIS_DICT_DEPOSIT = {'id': 0, 'state': 0, 'date': 0,
                      'operationAmount': {'amount': 0, 'currency': {'name': 0, 'code': 0}},
                      'description': 0, 'to': 0}
