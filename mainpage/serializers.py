from rest_framework import serializers
from .models import Player

class PlayerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(method_name='get_user_id')
    coin = serializers.IntegerField(read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'nick_name', 'coin']

    def get_user_id(self, player: Player):
        return player.user.id