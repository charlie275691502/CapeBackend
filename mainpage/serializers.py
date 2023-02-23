from rest_framework import serializers
from .models import Player

class PlayerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Player
        fields = ['nick_name', 'coin', 'user_id']