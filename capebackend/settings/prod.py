import os
import dj_database_url
import environ
from .common import *

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env('SECRET_KEY')

DEBUG = False

DATABASES = {
    'default': dj_database_url.parse(env('DATABASE_URL'))
}

# STATIC_HOST = os.environ.get("STATIC_HOST", "")
# STATIC_URL = STATIC_HOST + "/static/"