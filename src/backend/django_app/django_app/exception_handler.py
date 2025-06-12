from rest_framework.exceptions import  AuthenticationFailed, PermissionDenied
from rest_framework.exceptions import APIException
from rest_framework import views

class NotAuthenticatedError(AuthenticationFailed):
    pass
class InvalidSessionError(AuthenticationFailed):
    pass
class SessionExpiredError(PermissionDenied):
    pass
class UserInactiveError(PermissionDenied):
    pass

class CustomAPIException(APIException):
    def __init__(self,detail,status_code,message):
        self.status_code = status_code
        self.detail = {
            "message":message,
            "errors": detail or {}
        }



def custom_exception_handler(exc, context):
    response = views.exception_handler(exc, context)
    if isinstance(exc,NotAuthenticatedError):
        response.data = {
            "message": "Session cookie is missing",
            "errors": "",
        }
        response.status_code = 401
        return response
    if isinstance(exc,InvalidSessionError):
        response.data = {
            "message":"Session cookie is invalid",
            "errors":"",
        }
        response.status_code=401
        return response

    if isinstance(exc,SessionExpiredError):
        response.data = {
            "message":"Session cookies expired",
            "errors":"",
        }
        response.status_code=403
        return response
    if isinstance(exc,UserInactiveError):
        response.data = {
            "message":"User was inactive",
            "errors":"",
        }
        response.status_code=403
        return response
    if response is not None and isinstance(exc, APIException):
        if isinstance(getattr(exc, 'detail', None), dict) and "message" in exc.detail:
            return response

        response.data = {
            "message": "Request failed",
            "errors": response.data
        }

    return response