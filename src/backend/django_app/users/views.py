import time
from django.utils import timezone

from django.contrib.auth.views import logout_then_login
from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login,logout
# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import UserRegistrationSerializer, EmailLoginSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
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
    "id": "",
    "email": "",
    "username": "",
    "created_at": "" (UTC)
    }
    Errors:
    405 - bad http method
    400 - errors in input data: (only this field where error occurred):
    {
        "email": [
            ""
        ],
        "username": [
            ""
        ],
        "password": [
            ""
        ]
    }

    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
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
    {
        "non_field_errors": [
            "User do not exists"
        ]
    }

    {
        "non_field_errors": [
            "Password incorrect"
        ]
    }

    """
    serializer = EmailLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        ll = user.last_login
        login(request,user)
        return Response({
            "email":serializer.data.get("email"),
            "lastLoginAt":ll,
        })
    return Response(serializer.errors,status=status.HTTP_401_UNAUTHORIZED)

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def log_out_user(request):
    """
    POST /logout/
    Response when no errors: 204 code:

    Errors:
    405 - bad http method
    403 - logout when you are not logged in:
    {
        "detail": "Authentication credentials were not provided."
    }
    """
    user = request.user
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    logout(request)
    resp =  Response(status=status.HTTP_204_NO_CONTENT)
    resp.delete_cookie('sessionid')
    resp.delete_cookie('csrftoken')
    return resp

