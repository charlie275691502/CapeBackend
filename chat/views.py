from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from .serializers import RoomListSerializer, RoomSerializer, MessageSerializer
from .models import Room, Message

class RoomViewSet(ModelViewSet):
    queryset = Room.objects.prefetch_related('messages__player').all()

    def get_serializer_class(self):
        if self.action == 'list' :
            return RoomListSerializer
        else :
            return RoomSerializer

class MessageViewSet(ModelViewSet):
    serializer_class = MessageSerializer

    def get_serializer_context(self):
        return {'room_id': self.kwargs['room_pk'], 'player_id': self.request.user.id}

    def get_queryset(self):
        return Message.objects.filter(room_id=self.kwargs['room_pk']).all()