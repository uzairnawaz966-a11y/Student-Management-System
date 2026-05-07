from django.urls import path, include


urlpatterns = [
    path('api/v1/', include("user_auth.api.v1.urls")),
]