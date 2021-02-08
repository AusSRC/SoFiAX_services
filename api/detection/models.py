# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from run.models import Run
from instance.models import Instance


class Detection(models.Model):
    id = models.BigAutoField(primary_key=True)
    instance = models.ForeignKey(Instance, models.DO_NOTHING)
    run = models.ForeignKey(Run, models.DO_NOTHING)
    name = models.CharField(max_length=200)
    access_url = models.CharField(max_length=200)
    access_format = models.CharField(max_length=200)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    x_min = models.FloatField()
    x_max = models.FloatField()
    y_min = models.FloatField()
    y_max = models.FloatField()
    z_min = models.FloatField()
    z_max = models.FloatField()
    n_pix = models.FloatField()
    f_min = models.FloatField()
    f_max = models.FloatField()
    f_sum = models.FloatField()
    rel = models.FloatField(blank=True, null=True)
    rms = models.FloatField()
    w20 = models.FloatField()
    w50 = models.FloatField()
    ell_maj = models.FloatField()
    ell_min = models.FloatField()
    ell_pa = models.FloatField()
    ell3s_maj = models.FloatField()
    ell3s_min = models.FloatField()
    ell3s_pa = models.FloatField()
    kin_pa = models.FloatField(blank=True, null=True)
    ra = models.FloatField(blank=True, null=True)
    dec = models.FloatField(blank=True, null=True)
    l = models.FloatField(blank=True, null=True)
    b = models.FloatField(blank=True, null=True)
    v_rad = models.FloatField(blank=True, null=True)
    v_opt = models.FloatField(blank=True, null=True)
    v_app = models.FloatField(blank=True, null=True)
    err_x = models.FloatField()
    err_y = models.FloatField()
    err_z = models.FloatField()
    err_f_sum = models.FloatField()
    freq = models.FloatField(blank=True, null=True)
    flag = models.IntegerField(blank=True, null=True)
    unresolved = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'detection'
        unique_together = (('name', 'x', 'y', 'z', 'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max', 'n_pix', 'f_min', 'f_max', 'f_sum', 'instance', 'run'),)
