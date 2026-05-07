from django.urls import path
from user_auth.api.v1.views import (
    activate_account,
    RegisterUser,
    JWTLoginAPIView,
    ResendActivationLink,
    ChangePassword,
)


urlpatterns = [
    path("register-user/", RegisterUser.as_view(), name="register_user"),
    path("activate-user/<uuid:token>/", activate_account, name="activate_account"),
    path('login/', JWTLoginAPIView.as_view(), name="jwt_login"),
    path('resend-link/', ResendActivationLink.as_view(), name="resend_activation_link"),
    path('change-password/', ChangePassword.as_view(), name="change_password")
]