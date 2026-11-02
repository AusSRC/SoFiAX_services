from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class GaskapConfig(AppConfig):
    name = "modules.gaskap"
    verbose_name = "GASKAP-OH"

    def ready(self):
        from modules.core.signals import inspection_properties
        from modules.gaskap.receivers import gaskap_properties

        # The run page of this module replaces the one with the additions of the operations module
        if "operations" in settings.MODULES:
            raise ImproperlyConfigured("MODULES: gaskap cannot be used with operations")

        inspection_properties.connect(gaskap_properties)
