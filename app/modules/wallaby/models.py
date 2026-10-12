from django.db import models
from modules.core.models import Detection, Run
from modules.operations.models import Observation


class Tile(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()
    ra_deg = models.FloatField()
    dec_deg = models.FloatField()
    phase = models.TextField(null=True)
    description = models.TextField(null=True)
    image_cube_file = models.TextField(null=True)
    weights_cube_file = models.TextField(null=True)
    footprint_A = models.ForeignKey(
        Observation,
        on_delete=models.SET_NULL,
        db_column="footprint_A",
        related_name="footprint_A",
        to_field="id",
        null=True,
    )
    footprint_B = models.ForeignKey(
        Observation,
        on_delete=models.SET_NULL,
        db_column="footprint_B",
        related_name="footprint_B",
        to_field="id",
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = "tile"


class TileObs(models.Model):
    id = models.BigAutoField(primary_key=True)
    tile = models.ForeignKey(Tile, on_delete=models.DO_NOTHING, db_column="tile_id", to_field="id")
    obs = models.ForeignKey(Observation, on_delete=models.DO_NOTHING, db_column="obs_id", to_field="id")

    class Meta:
        managed = False
        db_table = "tile_obs"


class SourceExtractionRegion(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(null=True)
    ra_deg = models.FloatField(null=True)
    dec_deg = models.FloatField(null=True)
    complete = models.BooleanField(null=True)
    status = models.TextField(null=True)
    scheduled = models.BooleanField(null=True)
    run = models.ForeignKey(Run, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        managed = False
        db_table = "source_extraction_region"


class SourceExtractionRegionTile(models.Model):
    id = models.BigAutoField(primary_key=True)
    ser = models.ForeignKey(SourceExtractionRegion, on_delete=models.DO_NOTHING)
    tile = models.ForeignKey(Tile, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "source_extraction_region_tile"


class KinematicModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    detection = models.ForeignKey(Detection, models.DO_NOTHING)
    ra = models.FloatField()
    dec = models.FloatField()
    freq = models.FloatField()
    team_release = models.CharField(max_length=255)
    team_release_kin = models.CharField(max_length=255)
    vsys_model = models.FloatField()
    e_vsys_model = models.FloatField()
    x_model = models.FloatField()
    e_x_model = models.FloatField()
    y_model = models.FloatField()
    e_y_model = models.FloatField()
    ra_model = models.FloatField()
    e_ra_model = models.FloatField()
    dec_model = models.FloatField()
    e_dec_model = models.FloatField()
    inc_model = models.FloatField()
    e_inc_model = models.FloatField()
    pa_model = models.FloatField()
    e_pa_model = models.FloatField()
    pa_model_g = models.FloatField()
    e_pa_model_g = models.FloatField()
    qflag_model = models.IntegerField()
    rad = models.CharField(max_length=255)
    vrot_model = models.CharField(max_length=255)
    e_vrot_model = models.CharField(max_length=255)
    e_vrot_model_inc = models.CharField(max_length=255)
    rad_sd = models.CharField(max_length=255)
    sd_model = models.CharField(max_length=255)
    e_sd_model = models.CharField(max_length=255)
    sd_fo_model = models.CharField(max_length=255)
    e_sd_fo_model_inc = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "kinematic_model"


class KinematicModel_3KIDNAS(models.Model):
    id = models.BigAutoField(primary_key=True)
    detection = models.ForeignKey(Detection, models.DO_NOTHING)
    team_release = models.CharField(max_length=255)
    team_release_kin = models.CharField(max_length=255)
    vsys_model = models.FloatField()
    e_vsys_model = models.FloatField()
    x_model = models.FloatField()
    e_x_model = models.FloatField()
    y_model = models.FloatField()
    e_y_model = models.FloatField()
    ra_model = models.FloatField()
    e_ra_model = models.FloatField()
    dec_model = models.FloatField()
    e_dec_model = models.FloatField()
    inc_model = models.FloatField()
    e_inc_model = models.FloatField()
    pa_model = models.FloatField()
    e_pa_model = models.FloatField()
    pa_model_g = models.FloatField()
    e_pa_model_g = models.FloatField()
    vdisp_model = models.FloatField()
    e_vdisp_model = models.FloatField()
    rad = models.CharField(max_length=255)
    vrot_model = models.CharField(max_length=255)
    e_vrot_model = models.CharField(max_length=255)
    rad_sd = models.CharField(max_length=255)
    sd_model = models.CharField(max_length=255)
    e_sd_model = models.CharField(max_length=255)
    sdmethodflag = models.IntegerField()
    rhi_flag = models.FloatField()
    rhi_as = models.FloatField()
    rhi_low_as = models.FloatField()
    rhi_high_as = models.FloatField()
    dist_model = models.FloatField()
    rhi_kpc = models.FloatField()
    rhi_low_kpc = models.FloatField()
    rhi_high_kpc = models.FloatField()
    vhi_flag = models.IntegerField()
    vhi = models.FloatField()
    e_vhi = models.FloatField()
    kflag = models.IntegerField()
    kinver = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "kinematic_model_3kidnas"


class WKAPP_Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    kinematic_model = models.ForeignKey(
        KinematicModel, db_column="kinematic_model_id", to_field="id", on_delete=models.CASCADE
    )
    baroloinput = models.BinaryField(blank=True, null=True)
    barolomod = models.BinaryField(blank=True, null=True)
    barolosurfdens = models.BinaryField(blank=True, null=True)
    diagnosticplot = models.BinaryField(blank=True, null=True)
    diffcube = models.BinaryField(blank=True, null=True)
    fatinput = models.BinaryField(blank=True, null=True)
    fatmod = models.BinaryField(blank=True, null=True)
    fullresmodcube = models.BinaryField(blank=True, null=True)
    fullresproccube = models.BinaryField(blank=True, null=True)
    modcube = models.BinaryField(blank=True, null=True)
    procdata = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "wkapp_product"


class WRKP_Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    kinematic_model_3kidnas = models.ForeignKey(
        KinematicModel_3KIDNAS, db_column="kinematic_model_3kidnas", to_field="id", on_delete=models.CASCADE
    )
    bootstrapfits = models.BinaryField(blank=True, null=True)
    diagnosticplot = models.BinaryField(blank=True, null=True)
    diffcube = models.BinaryField(blank=True, null=True)
    flag = models.BinaryField(blank=True, null=True)
    modcube = models.BinaryField(blank=True, null=True)
    procdata = models.BinaryField(blank=True, null=True)
    pvmajordata = models.BinaryField(blank=True, null=True)
    pvmajormod = models.BinaryField(blank=True, null=True)
    pvminordata = models.BinaryField(blank=True, null=True)
    pvminormod = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "wrkp_product"


class KinematicModelState(models.Model):
    id = models.BigAutoField(primary_key=True)
    detection = models.ForeignKey(Detection, on_delete=models.CASCADE)
    attempted = models.IntegerField()

    class Meta:
        managed = False
        db_table = "kinematic_model_state"
