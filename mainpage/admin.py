from django.contrib import admin
from django.utils.html import format_html
from django.utils.http import urlencode
from django.urls import reverse
from . import models

# Register your models here.

@admin.register(models.Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['nick_name', 'coin', 'user_is_superuser', 'user_is_staff', 'user_link']
    list_editable = ['coin']
    list_select_related = ['user']

    def user_is_superuser(self, player: models.Player):
        return player.user.is_superuser

    def user_is_staff(self, player: models.Player):
        return player.user.is_staff

    def user_link(self, player: models.Player):
        url = reverse('admin:core_user_changelist') + '?' + urlencode({'player__user__id': player.user.id})
        return format_html('<a href="{}">{}</a>', url, player.user.username)