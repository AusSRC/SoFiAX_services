# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from detection.models import Detection


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    tag_name = models.CharField(unique=True, max_length=50)
    description = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tag'


class TagDetection(models.Model):
    id = models.BigAutoField(primary_key=True)
    tag = models.ForeignKey(Tag, models.DO_NOTHING)
    detection = models.ForeignKey(Detection, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'tag_detection'
