from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from .models import Player
from .serializers import PlayerSerializer

# Create your views here.
class PlayerViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request: Request):
        player, is_created = Player.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializer = PlayerSerializer(player)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = PlayerSerializer(player, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
