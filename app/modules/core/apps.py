from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "modules.core"
    # Label of the application before it was split into modules, so that the
    # admin urls and permissions of the core tables do not change
    label = "survey"
    verbose_name = "Survey"
