from rest_framework import serializers
from .models import BaseGameSetting

class BaseGameSettingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    game_type = serializers.CharField()
    player_plot = serializers.IntegerField()

    class Meta:
        model = BaseGameSetting
        fields = ['id', 'game_type', 'player_plot']