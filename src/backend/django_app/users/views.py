from django.utils import timezone
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import  login,logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView

from .serializers import UserRegistrationSerializer, EmailLoginSerializer
from django_app.utils import validate_or_raise

from django_app.exception_handler import CustomAPIException


class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        """
        POST /register/
        Request:
        {
        "email": "user@example.com",
        "username": "user123",
        "password": "strongpassword"
        }
        Response when no errors:
        {
        "email": "",
        "username": "",
        }
        Errors:
        405 - bad http method
        400 - errors in input data
        "message": "",
        "errors": {}
        """
        serializer = UserRegistrationSerializer(data=request.data)
        data = validate_or_raise(serializer,status_code=400,message="Register failed")
        serializer.save()
        return Response({
            "email":data["email"],
            "username":data["username"],
        })


class LoginUserView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        """
        POST /login/
        Request:
        {
        "email": "user@example.com",
        "password": "strongpassword"
        }

        Response when no errors:
        {
            "email": "",
            "lastLoginAt": ""
        }

        Errors:
        405 - bad http method
        401 - unauthorized:
        "message": "",
        "errors": {}

        """
        if request.user.is_authenticated:
            raise CustomAPIException(status_code=401,message="You are currently logged in",detail={})
        serializer = EmailLoginSerializer(data=request.data)
        data = validate_or_raise(serializer,status_code=401,message="Login failed")
        user = data['user']
        ll = user.last_login
        login(request,user)
        return Response({
            "email":data["email"],
            "lastLoginAt":ll,
        })

class LogoutUserView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        """
        POST /logout/
        Response when no errors: 204 code:
        Errors:
        405 - bad http method
        403 - logout when you are not logged in:
        "message": "",
        "errors": {}
        """
        user = request.user
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        logout(request)
        resp =  Response(status=status.HTTP_204_NO_CONTENT)
        resp.delete_cookie('sessionid')
        resp.delete_cookie('csrftoken')
        return resp

