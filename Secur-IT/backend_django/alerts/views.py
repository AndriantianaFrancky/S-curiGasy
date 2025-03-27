from rest_framework import generics
from .models import Alert
from .serializers import AlertSerializer

class AlertListCreate(generics.ListCreateAPIView):
    queryset = Alert.objects.all().order_by('-created_at')
    serializer_class = AlertSerializer
