from .base import *
from django.urls import path, include


ALLOWED_HOSTS = ['*']

MIDDLEWARE += [
    'silk.middleware.SilkyMiddleware'
]

INSTALLED_APPS += [
    'silk'
]
