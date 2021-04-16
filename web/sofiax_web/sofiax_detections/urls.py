from django.urls import path

from . import views


urlpatterns = [
    path(
        'detection_products',
        views.detection_products,
        name='detection_products'
    ),
    path(
        'instance_products',
        views.instance_products,
        name='instance_products'
    ),
    path(
        'run_products',
        views.run_products,
        name='run_products'
    ),
    path('catalog', views.run_catalog, name='run_catalog')
]
