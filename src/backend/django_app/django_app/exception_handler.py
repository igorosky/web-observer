from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

class CustomAPIException(APIException):
    def __init__(self,detail,status_code,message):
        self.status_code = status_code
        self.detail = {
            "message":message,
            "errors": detail or {}
        }



def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and isinstance(exc, APIException):
        if isinstance(getattr(exc, 'detail', None), dict) and "message" in exc.detail:
            return response

        response.data = {
            "message": "Request failed",
            "errors": response.data
        }

    return response