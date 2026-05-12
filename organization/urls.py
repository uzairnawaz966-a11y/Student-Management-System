from django.urls import path, include


urlpatterns = [
    path('api/v1/', include("organization.api.v1.urls"))
]