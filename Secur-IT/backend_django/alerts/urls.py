from django.urls import path
from .views import AlertListCreate

urlpatterns = [
    path('alerts/', AlertListCreate.as_view(), name='alert-list-create'),
]
