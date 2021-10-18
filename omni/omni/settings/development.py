from .base import *

ALLOWED_HOSTS = ['*']

MIDDLEWARE += [
    'silk.middleware.SilkyMiddleware'
]

INSTALLED_APPS += [
    'silk'
]
