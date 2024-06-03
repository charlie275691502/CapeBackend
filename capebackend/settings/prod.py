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
    'default': dj_database_url.parse(env('DATABASE_URL'))
}

STATIC_HOST = env("STATIC_HOST")
STATIC_URL = STATIC_HOST + "/static/"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [{
                "address": env("REDIS_EXTERNAL_IP"),
                "ssl_cert_reqs": None,
                       }],
        },
    },
}

INTERNAL_IPS = [
    '0.0.0.0',
]

CSRF_TRUSTED_ORIGINS = ['https://*.' + env("ALLOWED_HOST"), 'https://*.0.0.0.0']
CSRF_COOKIE_SECURE = False