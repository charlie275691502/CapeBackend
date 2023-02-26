from rest_framework import serializers
from core.serializers import UserSerializer
from .models import Player

class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    coin = serializers.IntegerField(read_only=True)

    class Meta:
        model = Player
        fields = ['nick_name', 'coin', 'user']