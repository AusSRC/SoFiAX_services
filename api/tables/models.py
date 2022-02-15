from django.db import models
import math
import cv2
import numpy as np
import binascii
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO, StringIO
from astropy.io import fits
from django.utils.safestring import mark_safe
from api.utils.fields import PostgresDecimalField


matplotlib.use('Agg')


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
        # TODO(austin): could pull this out of here by referencing SoFiAX
        if self.id == detect.id:
            raise ValueError('Same detection.')

        if self.run.id != detect.run.id:
            raise ValueError('Detection belongs to different run.')

        sanity_thresholds = self.run.sanity_thresholds

        f1 = self.f_sum
        f2 = detect.f_sum
        flux_threshold = sanity_thresholds['flux']
        diff = abs(f1 - f2) * 100 / ((abs(f1) + abs(f2)) / 2)

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
        if self.id == detect.id:
            raise ValueError('Same detection.')

        if self.run.id != detect.run.id:
            raise ValueError('Detection belongs to different run.')

        if self.x == detect.x and self.y == detect.y and self.z == detect.z:
            return True

        sanity = self.run.sanity_thresholds
        sigma = sanity.get('uncertainty_sigma', 5)

        d_space = math.sqrt(
            (self.x - detect.x) ** 2 + (self.y - detect.y) ** 2
        )
        d_space_err = math.sqrt(
            (self.x - detect.x) ** 2 * (self.err_x ** 2 + detect.err_x ** 2) +
            (self.y - detect.y) ** 2 * (self.err_y ** 2 + detect.err_y ** 2)) \
            / ((self.x - detect.x) ** 2 + (self.y - detect.y) ** 2)
        d_spec = abs(self.z - detect.z)
        d_spec_err = math.sqrt(self.err_z ** 2 + detect.err_z ** 2)

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

    class Meta:
        managed = False
        db_table = 'source'
        unique_together = (('name', ),)


class SourceDetection(models.Model):
    """Mapping from detections to sources

    """
    id = models.BigAutoField(primary_key=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    detection = models.ForeignKey(Detection, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'source_detection'
        unique_together = (('detection', ),)


class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, blank=True, null=True)
    auth_srid = models.IntegerField(blank=True, null=True)
    srtext = models.CharField(max_length=2048, blank=True, null=True)
    proj4text = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'spatial_ref_sys'


# ------------------------------------------------------------------------------
# Metadata tables

class RunMetadata(models.Model):
    id = models.BigAutoField(primary_key=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    repository = models.CharField(max_length=256)
    branch = models.CharField(max_length=256)
    version = models.CharField(max_length=32)
    configuration = models.JSONField()
    parameters = models.JSONField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'run_metadata'


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    comment = models.TextField()
    author = models.CharField(max_length=128)
    detection = models.ForeignKey(Detection, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comment'


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tag'


class TagDetection(models.Model):
    id = models.BigAutoField(primary_key=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    detection = models.ForeignKey(Detection, on_delete=models.CASCADE)
    author = models.TextField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tag_detection'
        unique_together = (('tag', 'detection'),)


class TagSourceDetection(models.Model):
    id = models.BigAutoField(primary_key=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    source_detection = models.ForeignKey(
        SourceDetection,
        on_delete=models.CASCADE
    )
    author = models.TextField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'tag_source_detection'
        unique_together = (('tag', 'source_detection'),)

# ------------------------------------------------------------------------------
