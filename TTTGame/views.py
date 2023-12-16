from rest_framework.viewsets import ModelViewSet
from .models import TTTRecord, TTTGame
from .serializers import TTTRecordSerializer, TTTGameSerializer

class TTTRecordViewSet(ModelViewSet):
    queryset = TTTRecord.objects.all()
    serializer_class = TTTRecordSerializer

class TTTGameViewSet(ModelViewSet):
    queryset = TTTGame.objects.all()
    serializer_class = TTTGameSerializer