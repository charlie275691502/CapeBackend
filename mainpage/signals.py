from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Player
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_player_for_new_player(sender, **kwargs):
    if kwargs['created'] :
        user = kwargs['instance']
        Player.objects.create(user=user, nick_name=user.username)