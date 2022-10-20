import io
import math
import cv2
import numpy as np
import binascii
import logging
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Ellipse
from io import BytesIO, StringIO
import astropy.units as u
from astropy.io import fits
from astropy.wcs import WCS
from astropy.visualization import PercentileInterval
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.safestring import mark_safe
from survey.utils.fields import PostgresDecimalField


matplotlib.use('Agg')
logging.basicConfig(level=logging.INFO)


# ------------------------------------------------------------------------------
# Astronomy data tables


class Run(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()
    sanity_thresholds = models.JSONField()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = False
        db_table = 'run'
        unique_together = (('name', 'sanity_thresholds'),)


class Instance(models.Model):
    """Automatically generated Django model from the WALLABY database.

    """
    id = models.BigAutoField(primary_key=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    filename = models.TextField()
    boundary = models.TextField()
    run_date = models.DateTimeField(auto_now_add=True)
    flag_log = models.BinaryField(blank=True, null=True)
    reliability_plot = models.BinaryField(blank=True, null=True)
    log = models.BinaryField(blank=True, null=True)
    parameters = models.JSONField()
    version = models.CharField(max_length=512, blank=True, null=True)
    return_code = models.IntegerField(null=True)
    stdout = models.BinaryField(blank=True, null=True)
    stderr = models.BinaryField(blank=True, null=True)

    def __unicode__(self):
        return f"{str(self.id)}"

    def __str__(self):
        return f"{str(self.id)}"

    class Meta:
        managed = False
        db_table = 'instance'
        unique_together = (('run', 'filename', 'boundary'),)


class Detection(models.Model):
    """Auto-generated Django model for WALLABY detection table.

    """
    id = models.BigAutoField(primary_key=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    name = models.TextField(blank=True, null=True)
    x = PostgresDecimalField()
    y = PostgresDecimalField()
    z = PostgresDecimalField()
    x_min = models.IntegerField(blank=True, null=True)
    x_max = models.IntegerField(blank=True, null=True)
    y_min = models.IntegerField(blank=True, null=True)
    y_max = models.IntegerField(blank=True, null=True)
    z_min = models.IntegerField(blank=True, null=True)
    z_max = models.IntegerField(blank=True, null=True)
    n_pix = models.IntegerField(blank=True, null=True)
    f_min = PostgresDecimalField(blank=True, null=True)
    f_max = PostgresDecimalField(blank=True, null=True)
    f_sum = PostgresDecimalField(blank=True, null=True)
    rel = PostgresDecimalField(blank=True, null=True)
    rms = PostgresDecimalField(blank=True, null=True)
    w20 = PostgresDecimalField(blank=True, null=True)
    w50 = PostgresDecimalField(blank=True, null=True)
    ell_maj = PostgresDecimalField(blank=True, null=True)
    ell_min = PostgresDecimalField(blank=True, null=True)
    ell_pa = PostgresDecimalField(blank=True, null=True)
    ell3s_maj = PostgresDecimalField(blank=True, null=True)
    ell3s_min = PostgresDecimalField(blank=True, null=True)
    ell3s_pa = PostgresDecimalField(blank=True, null=True)
    kin_pa = PostgresDecimalField(blank=True, null=True)
    err_x = PostgresDecimalField(blank=True, null=True)
    err_y = PostgresDecimalField(blank=True, null=True)
    err_z = PostgresDecimalField(blank=True, null=True)
    err_f_sum = PostgresDecimalField(blank=True, null=True)
    ra = PostgresDecimalField(blank=True, null=True)
    dec = PostgresDecimalField(blank=True, null=True)
    freq = PostgresDecimalField(blank=True, null=True)
    flag = models.IntegerField(blank=True, null=True)
    l = PostgresDecimalField(blank=True, null=True)  # noqa
    b = PostgresDecimalField(blank=True, null=True)
    v_rad = PostgresDecimalField(blank=True, null=True)
    v_opt = PostgresDecimalField(blank=True, null=True)
    v_app = PostgresDecimalField(blank=True, null=True)
    unresolved = models.BooleanField()
    wm50 = PostgresDecimalField(null=True)
    x_peak = models.IntegerField(null=True)
    y_peak = models.IntegerField(null=True)
    z_peak = models.IntegerField(null=True)
    ra_peak = PostgresDecimalField(null=True)
    dec_peak = PostgresDecimalField(null=True)
    freq_peak = PostgresDecimalField(null=True)
    l_peak = PostgresDecimalField(null=True)
    b_peak = PostgresDecimalField(null=True)
    v_rad_peak = PostgresDecimalField(null=True)
    v_opt_peak = PostgresDecimalField(null=True)
    v_app_peak = PostgresDecimalField(null=True)

    def __str__(self):
        return self.name

    def sanity_check(self, detect):
        logging.info(f'Running sanity check between detections {self.id} and {detect.id}')
        if self.id == detect.id:
            return False, 'Same detection.'

        if self.run.id != detect.run.id:
            return False, f'Detections {self.id} and {detect.id} belong to different runs.'

        sanity_thresholds = self.run.sanity_thresholds

        f1 = self.f_sum
        f2 = detect.f_sum
        flux_threshold = sanity_thresholds['flux']
        diff = abs(f1 - f2) * 100 / ((abs(f1) + abs(f2)) / 2)
        logging.info(f'Flux comparison: {f1} vs {f2}. Difference: {diff}')
        logging.info(f'Flux threshold: {flux_threshold}')

        if diff > flux_threshold:
            message = f"Detections: {self.id}, {detect.id} \
                Var: flux {round(diff, 2)}% > {flux_threshold}%"
            return False, message

        min_extent, max_extent = sanity_thresholds['spatial_extent']
        max1 = self.ell_maj
        max2 = detect.ell_maj
        min1 = self.ell_min
        min2 = detect.ell_min

        max_diff = abs(max1 - max2) * 100 / ((abs(max1) + abs(max2)) / 2)
        min_diff = abs(min1 - min2) * 100 / ((abs(min1) + abs(min2)) / 2)
        if max_diff > max_extent:
            return False, f"Detections: {self.id}, {detect.id} Var: ell_maj " \
                          f"Check: {round(max_diff, 2)}% > {max_extent}%"

        if min_diff > min_extent:
            return False, f"Detections: {self.id}, {detect.id} Var: ell_min " \
                          f"Check: {round(min_diff, 2)}% > {min_extent}%"

        min_extent, max_extent = sanity_thresholds['spectral_extent']
        max1 = self.w20
        max2 = detect.w20
        min1 = self.w50
        min2 = detect.w50
        max_diff = abs(max1 - max2) * 100 / ((abs(max1) + abs(max2)) / 2)
        min_diff = abs(min1 - min2) * 100 / ((abs(min1) + abs(min2)) / 2)
        if max_diff > max_extent:
            return False, f"Detections: {self.id}, {detect.id} Var: w20 " \
                          f"Check: {round(max_diff, 2)}% > {max_extent}%"

        if min_diff > min_extent:
            return False, f"Detections: {self.id}, {detect.id} Var: w50 " \
                          f"Check: {round(min_diff, 2)}% > {min_extent}%"

        return True, None

    def is_match(self, detect):
        logging.info(f'Checking if detections {self.id} and {detect.id} are matches')
        if self.id == detect.id:
            raise ValueError('Same detection.')

        if self.run.id != detect.run.id:
            raise ValueError(f'Detections {self.id} and {detect.id} belong to different runs.')

        if self.x == detect.x and self.y == detect.y and self.z == detect.z:
            return True

        sanity = self.run.sanity_thresholds
        sigma = sanity.get('uncertainty_sigma', 5)
        logging.info(f'Allowed uncertainty: {sigma}')

        d_space = math.sqrt(
            (self.x - detect.x) ** 2 + (self.y - detect.y) ** 2
        )
        logging.info(f'Spatial separation: {d_space}')
        d_space_err = math.sqrt(
            (self.x - detect.x) ** 2 * (self.err_x ** 2 + detect.err_x ** 2) +
            (self.y - detect.y) ** 2 * (self.err_y ** 2 + detect.err_y ** 2)) \
            / ((self.x - detect.x) ** 2 + (self.y - detect.y) ** 2)
        logging.info(f'Spatial separation error: {d_space_err}')
        d_spec = abs(self.z - detect.z)
        logging.info(f'Spectral separation: {d_spec}')
        d_spec_err = math.sqrt(self.err_z ** 2 + detect.err_z ** 2)
        logging.info(f'Spectral separation error: {d_spec_err}')
        logging.info(f'Spatial and spectral tests passing: ({d_space <= sigma * d_space_err}, {d_spec <= sigma * d_spec_err})')

        return d_space <= sigma * d_space_err and d_spec <= sigma * d_spec_err

    def spectrum_image(self):
        product = self.product_set.only('spec')
        if not product:
            return None

        x = []
        y = []
        with StringIO(product[0].spec.tobytes().decode('ascii')) as f:
            for line in f:
                li = line.strip()
                if not li.startswith("#"):
                    data = line.split()
                    x.append(float(data[1]))
                    y.append(float(data[2]))

        x = np.array(x)
        y = np.array(y)

        fig, ax = plt.subplots(nrows=1, ncols=1)
        fig.set_size_inches(2, 1)
        ax.plot(x, y, linewidth=1)
        ax.axhline(y.max() * .5, linewidth=1, color='r', alpha=0.5)
        ax.axhline(y.max() * .2, linewidth=1, color='r', alpha=0.5)
        ax.set_yticklabels([])
        ax.set_xticklabels([])

        with BytesIO() as image_data:
            fig.savefig(image_data, format='png')
            base_img = binascii.b2a_base64(image_data.getvalue()).decode()
            img_src = f'<img src=\"data:image/png;base64,{base_img}\">'
            plt.close(fig)
            return mark_safe(img_src)

    def moment0_image(self):
        product = self.product_set.only('mom0')
        if not product:
            return None

        with fits.open(BytesIO(product[0].mom0)) as hdu:
            data = hdu[0].data
            img = 255 * ((data - data.min()) / data.ptp())
            img = img.astype(np.uint8)
            img = cv2.applyColorMap(img, cv2.COLORMAP_HSV)
            img = Image.fromarray(img, 'RGB')
            img = img.resize(
                (hdu[0].header['NAXIS1'] * 2, hdu[0].header['NAXIS2'] * 2),
                Image.BICUBIC
            )
            with BytesIO() as image_file:
                img.save(image_file, format='PNG')
                image_data = image_file.getvalue()
                base_img = binascii.b2a_base64(image_data).decode()
                img_src = f'<img src=\"data:image/png;base64,{base_img}\">'
                return mark_safe(img_src)

    class Meta:
        managed = False
        db_table = 'detection'
        ordering = ("x",)
        unique_together = (('ra', 'dec', 'freq', 'instance', 'run'),)


class UnresolvedDetection(Detection):
    class Meta:
        proxy = True


class InternalConflictSource(Detection):
    class Meta:
        proxy = True


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    detection = models.ForeignKey(Detection, on_delete=models.CASCADE)
    cube = models.BinaryField(blank=True, null=True)
    mask = models.BinaryField(blank=True, null=True)
    mom0 = models.BinaryField(blank=True, null=True)
    mom1 = models.BinaryField(blank=True, null=True)
    mom2 = models.BinaryField(blank=True, null=True)
    chan = models.BinaryField(blank=True, null=True)
    snr = models.BinaryField(blank=True, null=True)
    spec = models.BinaryField(blank=True, null=True)
    summary = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product'
        unique_together = (('detection',),)


class Source(models.Model):
    """Subset of quality checked detections to include in the
    final source catalog.

    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = False
        db_table = 'source'
        unique_together = (('name', ),)


class SourceDetection(models.Model):
    id = models.BigAutoField(primary_key=True)
    source = models.ForeignKey(Source, models.DO_NOTHING)
    detection = models.OneToOneField(Detection, models.DO_NOTHING)
    added_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.source}, {self.detection}"

    class Meta:
        managed = False
        db_table = 'source_detection'


class ExternalConflict(models.Model):
    id = models.BigAutoField(primary_key=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    detection = models.ForeignKey(Detection, on_delete=models.CASCADE)
    conflict_source_detection_ids = ArrayField(
        models.IntegerField()
    )

    class Meta:
        managed = False
        db_table = 'external_conflict'


class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, blank=True, null=True)
    auth_srid = models.IntegerField(blank=True, null=True)
    srtext = models.CharField(max_length=2048, blank=True, null=True)
    proj4text = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'spatial_ref_sys'


class KinematicModel(models.Model):
    id = models.BigAutoField(db_column='ID', primary_key=True)
    name = models.ForeignKey('Source', models.DO_NOTHING, db_column='Name', to_field='name')
    ra = models.FloatField(db_column='RA')
    dec = models.FloatField(db_column='DEC')
    freq = models.FloatField()
    team_release = models.CharField(max_length=255)
    team_release_kin = models.CharField(max_length=255)
    vsys_model = models.FloatField(db_column='Vsys_model')
    e_vsys_model = models.FloatField(db_column='e_Vsys_model')
    x_model = models.FloatField(db_column='X_model')
    e_x_model = models.FloatField(db_column='e_X_model')
    y_model = models.FloatField(db_column='Y_model')
    e_y_model = models.FloatField(db_column='e_Y_model')
    ra_model = models.FloatField(db_column='RA_model')
    e_ra_model = models.FloatField(db_column='e_RA_model')
    dec_model = models.FloatField(db_column='DEC_model')
    e_dec_model = models.FloatField(db_column='e_DEC_model')
    inc_model = models.FloatField(db_column='Inc_model')
    e_inc_model = models.FloatField(db_column='e_Inc_model')
    pa_model = models.FloatField(db_column='PA_model')
    e_pa_model = models.FloatField(db_column='e_PA_model')
    pa_model_g = models.FloatField(db_column='PA_model_g')
    e_pa_model_g = models.FloatField(db_column='e_PA_model_g')
    qflag_model = models.IntegerField(db_column='QFlag_model')
    rad = models.CharField(db_column='Rad', max_length=255)
    vrot_model = models.CharField(db_column='Vrot_model', max_length=255)
    e_vrot_model = models.CharField(db_column='e_Vrot_model', max_length=255)
    e_vrot_model_inc = models.CharField(db_column='e_Vrot_model_inc', max_length=255)
    rad_sd = models.CharField(db_column='Rad_SD', max_length=255)
    sd_model = models.CharField(db_column='SD_model', max_length=255)
    e_sd_model = models.CharField(db_column='e_SD_model', max_length=255)
    sd_fo_model = models.CharField(db_column='SD_FO_model', max_length=255)
    e_sd_fo_model_inc = models.CharField(db_column='e_SD_FO_model_inc', max_length=255)

    class Meta:
        managed = False
        db_table = 'kinematic_model'

# ------------------------------------------------------------------------------
# Metadata tables


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    comment = models.TextField()
    author = models.CharField(max_length=2048, blank=True, null=True)
    detection = models.ForeignKey('Detection', models.DO_NOTHING)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        managed = False
        db_table = 'comment'


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = False
        db_table = 'tag'


class TagSourceDetection(models.Model):
    id = models.BigAutoField(primary_key=True)
    tag = models.ForeignKey(Tag, models.DO_NOTHING)
    source_detection = models.ForeignKey(SourceDetection, models.DO_NOTHING)
    author = models.CharField(max_length=2048, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tag_source_detection'

# ------------------------------------------------------------------------------
