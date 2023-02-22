from rest_framework import serializers
from .models import Player

class PlayerSerializers(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Player
        fields = ['nick_name', 'coin', 'user_id']