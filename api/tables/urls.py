from django.urls import path
from tables.views import detection_products, instance_products, \
    run_products, run_catalog


urlpatterns = [
    path('detection_products', detection_products, name='detection_products'),
    path('instance_products', instance_products, name='instance_products'),
    path('run_products', run_products, name='run_products'),
    path('catalog', run_catalog, name='run_catalog')
]
