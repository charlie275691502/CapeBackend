from rest_framework import serializers
from core.serializers import UserSerializer
from .models import Player

class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Player
        fields = ['nick_name', 'coin', 'user']