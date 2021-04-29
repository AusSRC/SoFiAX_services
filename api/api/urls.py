from django.contrib import admin
from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView
from django.conf import settings

from tables.views import detection_products, instance_products, \
    run_products, run_catalog

admin.site.site_header = settings.SITE_HEADER
admin.site.site_title = settings.SITE_TITLE
admin.site.index_title = settings.INDEX_TITLE

urlpatterns = [
    path('detection_products', detection_products, name='detection_products'),
    path('instance_products', instance_products, name='instance_products'),
    path('run_products', run_products, name='run_products'),
    path('catalog', run_catalog, name='run_catalog'),
    path('', RedirectView.as_view(url=reverse_lazy('admin:index'))),
    path('admin/', admin.site.urls),
]

admin.site.enable_nav_sidebar = False
