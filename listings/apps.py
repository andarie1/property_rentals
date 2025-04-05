import importlib
from django.apps import AppConfig


class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'listings'

    def ready(self):
        importlib.import_module('listings.signals')