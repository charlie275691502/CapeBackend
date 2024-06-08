from rest_framework.viewsets import ModelViewSet
from .models import GOARecord, GOAGame
from .serializers import GOARecordSerializer, GOAGameSerializer

class GOARecordViewSet(ModelViewSet):
    queryset = GOARecord.objects.all()
    serializer_class = GOARecordSerializer

class GOAGameViewSet(ModelViewSet):
    queryset = GOAGame.objects.all()
    serializer_class = GOAGameSerializer