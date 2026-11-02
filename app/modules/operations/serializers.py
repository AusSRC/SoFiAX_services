from modules.operations.models import Observation
from rest_framework import serializers, viewsets


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = ["id", "sbid", "ra", "dec", "status", "accepted"]


class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.filter(sbid__isnull=False)
    serializer_class = ObservationSerializer
