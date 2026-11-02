from modules.core.models import Detection
from django.db import models


class DetectionNearestGAMA(models.Model):
    id = models.BigAutoField(primary_key=True)
    detection_id = models.ForeignKey(Detection, models.DO_NOTHING, db_column="detection_id", to_field="id")
    cata_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = "detection_nearest_gama"
