import os
import dj_database_url
import environ
from .common import *

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

DATABASES = {
    'default': dj_database_url.parse(env('DATABASE_URL'))
}

STATIC_HOST = os.environ.get("STATIC_HOST", "")
STATIC_URL = STATIC_HOST + "/static/"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("0.0.0.0", 6379)],
        },
    },
}