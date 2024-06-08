import os
import dj_database_url
import environ
from .common import *

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = [env("ALLOWED_HOST")]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'capebackend',
        'HOST': 'localhost',
        'USER': 'postgres',
        'PASSWORD': env('DATABASE_PASSWORD'),
    }
}

STATIC_HOST = env("STATIC_HOST")
STATIC_URL = STATIC_HOST + "/static/"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

INTERNAL_IPS = [
    '127.0.0.1',
]

CSRF_TRUSTED_ORIGINS = ['https://*.' + env("ALLOWED_HOST"), 'https://*.127.0.0.1']
CSRF_COOKIE_SECURE = False