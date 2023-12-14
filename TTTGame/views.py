from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from .serializers import TTTRecordSerializer, TTTGameSerializer

class TTTRecordViewSet(ModelViewSet):
    serializer_class = TTTRecordSerializer

class TTTGameViewSet(ModelViewSet):
    serializer_class = TTTGameSerializer