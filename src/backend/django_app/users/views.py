from django.utils import timezone
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import  login,logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from datetime import timedelta
from .serializers import UserRegistrationSerializer, EmailLoginSerializer
from django_app.utils import validate_or_raise
from .models import  User
from django_app.exception_handler import CustomAPIException
from django_app.custom_session import CustomSessionAuthentication
from django_app.custom_authentication import CustomIsAuthenticated


class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
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
        "userId":""
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
        serializer = validate_or_raise(serializer,status_code=400,message="Register failed")
        serializer.save()
        return Response({
            "userId":serializer.data["id"],
            "email":serializer.validated_data["email"],
            "username":serializer.validated_data["username"],
        })
#validated_data -> to co przyszlo od usera i zostalo sprawdzone/dodane w validate
#data -> ma wszystkie pola z fields

class LoginUserView(APIView):
    authentication_classes = []
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
            "userId":" "
            "email": " ",
            "lastLoginAt": " "
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
        serializer = validate_or_raise(serializer,status_code=401,message="Login failed")
        user = serializer.validated_data['user']
        ll = user.last_login
        login(request,user)
        resp =  Response({
            "userId":user.id,
            "email":serializer.validated_data["email"],
            "lastLoginAt":ll,
        })
        resp.set_cookie(
            key="was_logged_in",
            value="1",
            max_age=10000,#change to 2*value in settings
            secure=False#change to true on prods
        )
        return resp

class LogoutUserView(APIView):
    authentication_classes = [CustomSessionAuthentication]
    permission_classes = [CustomIsAuthenticated]
    def post(self,request):
        """
        POST /logout/
        Response when no errors: 204 code:
        Errors:
        405 - bad http method
        401 - logout when you are not logged in: # we have to do it because we
        need to have access to user -> update last login

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
        resp.delete_cookie('was_logged_in')
        return resp

