from django.urls import path
from .views import RegisterUserView,LoginUserView,LogoutUserView

urlpatterns = [
    path("register/",RegisterUserView.as_view(),name="register_user"),
    path("login/",LoginUserView.as_view(),name="login_user"),
    path("logout/",LogoutUserView.as_view(),name="log_out_user"),
]