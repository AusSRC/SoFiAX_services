from django.urls import path

from modules.operations.serializers import ObservationViewSet
from modules.operations.views import external_conflict_view

urlpatterns = [
    path("external_conflict", external_conflict_view, name="external_conflict"),
]

# REST API endpoints as (prefix, viewset, basename)
api_routes = [
    ("observations", ObservationViewSet, "observations"),
]
