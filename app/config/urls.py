from importlib import import_module
from importlib.util import find_spec

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView
from rest_framework import routers

admin.site.site_header = settings.SITE_HEADER
admin.site.site_title = settings.SITE_TITLE
admin.site.index_title = settings.INDEX_TITLE

admin.autodiscover()

# Views and REST API endpoints of the installed modules (urls.py of each module)
urlpatterns = []
router = routers.DefaultRouter()
for module in settings.MODULES:
    if find_spec(f"modules.{module}.urls") is None:
        continue
    urls = import_module(f"modules.{module}.urls")
    urlpatterns += urls.urlpatterns
    for prefix, viewset, basename in getattr(urls, "api_routes", []):
        router.register(prefix, viewset, basename=basename)

urlpatterns += [
    path("api/", include(router.urls)),
    path("", RedirectView.as_view(url=reverse_lazy("admin:index"))),
    path("admin/", admin.site.urls),
]

admin.site.enable_nav_sidebar = False
