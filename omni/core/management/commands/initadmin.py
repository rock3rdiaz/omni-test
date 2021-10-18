import environ

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env()


class Command(BaseCommand):
    def handle(self, *args, **options):
        username = env('DJANGO_SUPERUSER_USERNAME')
        email = env('DJANGO_SUPERUSER_EMAIL')
        password = env('DJANGO_SUPERUSER_PASSWORD')
        if not User.objects.filter(username=username).exists():
            print(f'Creating account for {username} {email}')
            User.objects.create_superuser(email=email, username=username, password=password)
        else:
            print('Admin account has already been initialized.')