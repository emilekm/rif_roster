from django.apps import AppConfig
from django.conf import settings


class SVAuthConfig(AppConfig):
    name = 'svauth'

    def ready(self):
        from svauth.models import Provider

        for provider in settings.AUTH_PROVIDERS:
            Provider.objects.get_or_create(name=provider)

