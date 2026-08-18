from survey.models import Observation, Tile, SourceExtractionRegion, SourceExtractionRegionTile
from rest_framework import serializers, viewsets
from django.db.models import F


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = ["id", "sbid", "ra", "dec", "status", "accepted"]


class TileSerializer(serializers.ModelSerializer):
    """Get all fields for Tile object.
    Additionally fetch status of footprint A and B from foreign key relationship.

    """
    a_status = serializers.SerializerMethodField('get_a_status')
    b_status = serializers.SerializerMethodField('get_b_status')

    def get_a_status(self, obj):
        return obj.footprint_A.status if obj.footprint_A else None

    def get_b_status(self, obj):
        return obj.footprint_B.status if obj.footprint_B else None

    class Meta:
        model = Tile
        fields = [
            "id",
            "name",
            "ra_deg",
            "dec_deg",
            "phase",
            "footprint_A",
            "footprint_B",
            "a_status",
            "b_status",
        ]


class SourceExtractionRegionSerializer(serializers.ModelSerializer):
    sbids = serializers.SerializerMethodField('get_sbids')

    class Meta:
        model = SourceExtractionRegion
        fields = ["id", "name", "ra_deg", "dec_deg", "status", "sbids", "complete", "scheduled"]

    def get_sbids(self, obj):
        sert = SourceExtractionRegionTile.objects.filter(ser=obj)
        if sert.exists():
            tiles = Tile.objects.filter(id__in=sert.values_list('tile_id', flat=True))
            obs_pairs = [[t.footprint_A, t.footprint_B] for t in tiles]
            obs = sum(obs_pairs, [])
            sbids = [o.sbid for o in obs if o.sbid is not None]
            sbids.sort()
        sbids_str = ', '.join(str(sbid) for sbid in sbids) if sbids else None
        return sbids_str


class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observation.objects.filter(sbid__isnull=False)
    serializer_class = ObservationSerializer


class TileViewSet(viewsets.ModelViewSet):
    queryset = Tile.objects.filter(phase="Survey")
    serializer_class = TileSerializer


class SourceExtractionRegionViewSet(viewsets.ModelViewSet):
    queryset = SourceExtractionRegion.objects.all()
    serializer_class = SourceExtractionRegionSerializer
