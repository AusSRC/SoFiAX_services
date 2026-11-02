from django.apps import AppConfig


class WallabyConfig(AppConfig):
    name = "modules.wallaby"
    verbose_name = "WALLABY"

    def ready(self):
        from modules.operations.signals import detection_released
        from modules.wallaby.receivers import mark_for_kinematic_modelling

        detection_released.connect(mark_for_kinematic_modelling)
