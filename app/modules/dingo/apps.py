from django.apps import AppConfig


class DingoConfig(AppConfig):
    name = "modules.dingo"
    verbose_name = "DINGO"

    def ready(self):
        from modules.core.signals import inspection_matches
        from modules.dingo.receivers import gama_matches

        inspection_matches.connect(gama_matches)
