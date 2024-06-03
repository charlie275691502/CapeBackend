import dj_database_url
import environ
from .common import *

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'capebackend',
        'HOST': 'localhost',
        'USER': 'postgres',
        'PASSWORD': '6805',
    }
}

# DATABASES = {
#     'default': dj_database_url.parse(env('DATABASE_URL'))
# }

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