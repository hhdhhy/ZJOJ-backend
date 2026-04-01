from django.urls import path
from rest_framework.urls import app_name

from apps.ojauth.views import LoginView

app_name = "ojauth"
urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
]
