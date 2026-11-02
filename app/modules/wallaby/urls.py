from django.urls import path

from modules.wallaby.serializers import SourceExtractionRegionViewSet, TileViewSet
from modules.wallaby.views import wkapp_products, wrkp_products

urlpatterns = [
    path("wkapp_products", wkapp_products, name="wkapp_products"),
    path("wrkp_products", wrkp_products, name="wrkp_products"),
]

# REST API endpoints as (prefix, viewset, basename)
api_routes = [
    ("tiles", TileViewSet, "tiles"),
    ("sers", SourceExtractionRegionViewSet, "source_extraction_regions"),
]
