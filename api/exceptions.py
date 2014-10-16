from rest_framework.exceptions import APIException

class NotEnoughMoney(APIException):
    status_code = 402
    detail = 'Not enough balance'