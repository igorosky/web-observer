from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import  login,logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, EmailLoginSerializer
from django_app.utils import validate_or_raise
from django_app.exception_handler import CustomAPIException
from django_app.custom_session import CustomSessionAuthentication
from django_app.custom_authentication import CustomIsAuthenticated


class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self,request):
        """
        POST /register/
        """
        serializer = UserRegistrationSerializer(data=request.data)
        serializer = validate_or_raise(serializer,status_code=400,message="Register failed")
        serializer.save()
        return Response({
            "userId":serializer.data["id"],
            "email":serializer.validated_data["email"],
            "username":serializer.validated_data["username"],
        })

class LoginUserView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self,request):
        """
        POST /login/
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
            "username":user.username,
            "lastLoginAt":ll,
        })
        resp.set_cookie(
            key="was_logged_in",
            value="1",
            max_age=10000,
            secure=False
        )
        return resp


class LogoutUserView(APIView):
    """
      POST /logout/
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

        logout(request)

        resp = Response(status=status.HTTP_204_NO_CONTENT)
        resp.delete_cookie('sessionid')
        resp.delete_cookie('csrftoken')
        resp.delete_cookie('was_logged_in')
        return resp