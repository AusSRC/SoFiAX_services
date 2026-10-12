import ast
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from modules.core.models import Detection, Run


# ------------------------------------------------------------------------------
# Operational tables


class ExternalConflict(models.Model):
    id = models.BigAutoField(primary_key=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    detection = models.ForeignKey(
        Detection, db_column="detection_id", related_name="detection", to_field="id", on_delete=models.CASCADE
    )
    conflict_detection = models.ForeignKey(
        Detection,
        db_column="conflict_detection_id",
        related_name="conflict_detection",
        to_field="id",
        on_delete=models.CASCADE,
    )

    class Meta:
        managed = False
        db_table = "external_conflict"


class Observation(models.Model):
    id = models.BigAutoField(primary_key=True)
    run = models.ForeignKey(Run, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.TextField()
    sbid = models.CharField(max_length=64, null=True)
    ra = models.FloatField()
    dec = models.FloatField()
    rotation = models.FloatField(null=True)
    description = models.TextField(null=True, blank=True)
    phase = models.CharField(max_length=64, null=True)
    image_cube_file = models.TextField(null=True)
    weights_cube_file = models.TextField(null=True)
    quality = models.CharField(max_length=64, null=True)
    status = models.CharField(max_length=64, null=True)
    scheduled = models.BooleanField(null=True)
    accepted = models.BooleanField(null=True, blank=True)
    flags = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        """Validate the format of the flags field, which should be a list of regions defined by (x1,x2,y1,y2,z1,z2)"""
        # TODO: refactor into common util function
        try:
            flags = self.flags
            region_list = flags.split(";")
            region_list = [ast.literal_eval(r.strip()) for r in flags.split(";") if r.strip()]
        except (ValueError, SyntaxError):
            raise ValidationError("Invalid format for flags field. Use (x1,x2,y1,y2,z1,z2); (x1,x2,y1,y2,z1,z2); ...")
        for region in region_list:
            if len(region) != 6:
                raise ValidationError("Flag region should have 6 values: (x1,x2,y1,y2,z1,z2) separeted by semicolon")
            x1, x2, y1, y2, z1, z2 = region
            if not (x1 < x2 and y1 < y2 and z1 < z2):
                raise ValidationError("Flag region values should satisfy x1 < x2, y1 < y2, z1 < z2")

    class Meta:
        managed = False
        db_table = "observation"


class SurveyComponent(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=2048, blank=True, null=True)
    runs = ArrayField(models.TextField(), editable=False)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "survey_component"


class SurveyComponentRun(models.Model):
    id = models.BigAutoField(primary_key=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    sc = models.ForeignKey(SurveyComponent, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "survey_component_run"
        unique_together = (("run", "sc"),)
