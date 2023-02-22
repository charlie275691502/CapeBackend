from django.db import models
from django.conf import settings

# Create your models here.
class Player(models.Model):
    nick_name = models.CharField(max_length=20)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)