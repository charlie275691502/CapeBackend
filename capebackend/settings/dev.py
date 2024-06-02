import dj_database_url
import environ
from .common import *

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'capebackend',
        'HOST': 'localhost',
        'USER': 'postgres',
        'PASSWORD': '6805',
    }
}