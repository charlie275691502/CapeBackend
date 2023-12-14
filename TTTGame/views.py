from rest_framework.viewsets import ModelViewSet
from .serializers import TTTRecordSerializer, TTTGameSerializer

class TTTRecordViewSet(ModelViewSet):
    serializer_class = TTTRecordSerializer

class TTTGameViewSet(ModelViewSet):
    serializer_class = TTTGameSerializer