# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from detection.models import Detection


class Products(models.Model):
    id = models.BigAutoField(primary_key=True)
    detection = models.OneToOneField(Detection, models.DO_NOTHING)
    cube = models.BinaryField(blank=True, null=True)
    mask = models.BinaryField(blank=True, null=True)
    moment0 = models.BinaryField(blank=True, null=True)
    moment1 = models.BinaryField(blank=True, null=True)
    moment2 = models.BinaryField(blank=True, null=True)
    channels = models.BinaryField(blank=True, null=True)
    spectrum = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'
