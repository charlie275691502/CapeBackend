from rest_framework import serializers
from mainpage.serializers import PlayerSerializer
from .models import Room, Message

class MessageSerializer(serializers.ModelSerializer):
    player_id = serializers.IntegerField(read_only=True)

    def save(self, **kwargs):
        room_id = self.context['room_id']
        player_id = self.context['player_id']
        Message.objects.create(room_id=room_id, player_id=player_id, **self.validated_data)

    class Meta:
        model = Message
        fields = ['id', 'content', 'create_at', 'player_id']

class RoomListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    players = PlayerSerializer(read_only=True, many=True)

    class Meta:
        model = Room
        fields = ['id', 'room_name', 'players']


class RoomSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    players = PlayerSerializer(read_only=True, many=True)
    messages = MessageSerializer(read_only=True, many=True)

    class Meta:
        model = Room
        fields = ['id', 'room_name', 'players', 'messages']