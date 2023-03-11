from rest_framework import serializers
from mainpage.serializers import PlayerSerializer
from .models import Room, Message
from mainpage.models import Player

class MessagePlayerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name='get_user_id')

    class Meta:
        model = Player
        fields = ['id', 'nick_name']

    def get_user_id(self, player: Player):
        return player.user.id

class MessageSerializer(serializers.ModelSerializer):
    player = MessagePlayerSerializer(read_only=True)

    def save(self, **kwargs):
        room_id = self.context['room_id']
        player_id = self.context['player_id']
        Message.objects.create(room_id=room_id, player_id=player_id, **self.validated_data)

    class Meta:
        model = Message
        fields = ['id', 'content', 'create_at', 'player']

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