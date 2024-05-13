import os
import math
import json
import cv2
import numpy as np
import binascii
import logging
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt

from enum import IntEnum
from io import BytesIO, StringIO
from astropy.io import fits
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import format_html
from django.conf import settings


from survey.utils.fields import PostgresDecimalField
from survey.utils.plot import product_summary_image


matplotlib.use('Agg')
logging.basicConfig(level=logging.INFO)


class TaskReturnType(IntEnum):
    NONE = 1
    FILE = 2
    VALUE = 3


class TaskReturn(object):
    def __init__(self, return_type, return_values):
        if return_values is None:
            raise ValueError("None return_values")
        self.return_type = return_type
        self.return_values = return_values

    def __str__(self):
        return self.return_values

    def get_link(self, task):
        return None

    def get_json(self):
        return json.dumps({'type': self.return_type, 'retval': self.return_values})

    def cleanup(self):
        pass


class NoneTaskReturn(TaskReturn):
    def __init__(self):
        super(NoneTaskReturn, self).__init__(int(TaskReturnType.NONE), "")

    def __str__(self):
        return None


class FileTaskReturn(TaskReturn):
    def __init__(self, file_paths):
        if not isinstance(file_paths, list):
            raise ValueError("file paths must be a list")

        super(FileTaskReturn, self).__init__(int(TaskReturnType.FILE), file_paths)

    def __str__(self):
        return ','.join([os.path.basename(f) for f in self.return_values])

    def get_paths(self):
        return self.return_values

    def get_link(self, task):
        url = reverse('task_file_download')
        return format_html(f"<a href='{url}?id={task.id}'>Download</a>")

    def cleanup(self):
        for f in self.return_values:
            try:
                os.remove(f)
            except Exception as e:
                pass


class ValueTaskReturn(TaskReturn):
    def __init__(self, value):
        super(ValueTaskReturn, self).__init__(int(TaskReturnType.VALUE), value)


class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    func = models.TextField()
    queryset = models.JSONField()
    args = models.JSONField()
    retval = models.JSONField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    error = models.TextField()
    state = models.TextField()
    user = models.TextField()

    def __str__(self):
        return f"{self.id}"

    def get_return_link(self):
        ret = self.get_return()
        if ret:
            if self.state == 'COMPLETED':
                return ret.get_link(self)
        return None

    def get_return(self):
        if self.retval is None:
            return None
        retval = json.loads(self.retval)
        rettype = retval['type']

        if rettype == int(TaskReturnType.NONE):
            return NoneTaskReturn(retval['retval'])
        elif rettype == int(TaskReturnType.FILE):
            return FileTaskReturn(retval['retval'])
        elif rettype == int(TaskReturnType.VALUE):
            return ValueTaskReturn(retval['retval'])
        else:
            raise ValueError("Unknown return type")

    class Meta:
        managed = False
        db_table = 'task'

# ------------------------------------------------------------------------------
# Astronomy data tables


class Run(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()
    sanity_thresholds = models.JSONField()
    created = models.DateTimeField()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = False
        db_table = 'run'
        unique_together = (('name', 'sanity_thresholds'),)


class Instance(models.Model):
    """Automatically generated Django model from the database.

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
    """Auto-generated Django model for detection table.

    """
    id = models.BigAutoField(primary_key=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    name = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
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
    l = PostgresDecimalField(blank=True, null=True)
    b = PostgresDecimalField(blank=True, null=True)
    v_rad = PostgresDecimalField(blank=True, null=True)
    v_opt = PostgresDecimalField(blank=True, null=True)
    v_app = PostgresDecimalField(blank=True, null=True)
    unresolved = models.BooleanField()
    accepted = models.BooleanField(default=False)
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

        if not x or not y:
            return None

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
            img_src = f'<img src=\"data:image/png;base64,{base_img}\", style="border-radius: 3%;">'
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
                img_src = f'<img src=\"data:image/png;base64,{base_img}\", style="border-radius: 3%;">'
                return mark_safe(img_src)

    def summary_image(self, size=(3, 2), binary_image=False):
        products = self.product_set.only('spec')
        if not products:
            return None
        return product_summary_image(products[0], size=size, binary_image=binary_image)

    def description_string(self):
        description = ''
        description += ', '.join([td.tag.name for td in TagDetection.objects.filter(detection_id=self.id)])
        description += ', '.join([c.comment for c in Comment.objects.filter(detection_id=self.id)])
        if description == '':
            description = 'No tags or comments'
        return description

    class Meta:
        managed = False
        db_table = 'detection'
        ordering = ("x",)
        unique_together = (('ra', 'dec', 'freq', 'instance', 'run'),)


class AcceptedDetection(Detection):
    class Meta:
        proxy = True


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
    pv = models.BinaryField(blank=True, null=True)
    plot = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product'
        unique_together = (('detection',),)


# ------------------------------------------------------------------------------
# Metadata tables

class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    comment = models.TextField()
    author = models.CharField(max_length=2048, blank=True, null=True)
    detection = models.ForeignKey('Detection', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        managed = False
        db_table = 'comment'


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        managed = False
        db_table = 'tag'


class TagDetection(models.Model):
    id = models.BigAutoField(primary_key=True)
    tag = models.ForeignKey(Tag, models.CASCADE)
    detection = models.ForeignKey(Detection, on_delete=models.CASCADE)
    author = models.CharField(max_length=2048, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        managed = False
        db_table = 'tag_detection'
        unique_together = (('tag', 'detection'),)


# ------------------------------------------------------------------------------
# Operational tables

class ExternalConflict(models.Model):
    id = models.BigAutoField(primary_key=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    detection = models.ForeignKey(Detection, db_column='detection_id', related_name='detection', to_field='id', on_delete=models.CASCADE)
    conflict_detection = models.ForeignKey(Detection, db_column='conflict_detection_id', related_name='conflict_detection', to_field='id', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'external_conflict'


class Observation(models.Model):
    id = models.BigAutoField(primary_key=True)
    run = models.ForeignKey(Run, on_delete=models.SET_NULL, null=True)
    name = models.TextField()
    sbid = models.CharField(max_length=64, null=True)
    ra = models.FloatField()
    dec = models.FloatField()
    rotation = models.FloatField(null=True)
    description = models.TextField(null=True)
    phase = models.CharField(max_length=64, null=True)
    image_cube_file = models.TextField(null=True)
    weights_cube_file = models.TextField(null=True)
    quality = models.CharField(max_length=64, null=True)
    status = models.CharField(max_length=64, null=True)
    scheduled = models.BooleanField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'observation'


class Tile(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()
    ra_deg = models.FloatField()
    dec_deg = models.FloatField()
    phase = models.TextField(null=True)
    description = models.TextField(null=True)
    image_cube_file = models.TextField(null=True)
    weights_cube_file = models.TextField(null=True)
    footprint_A = models.ForeignKey(Observation, on_delete=models.SET_NULL, db_column='footprint_A', related_name='footprint_A', to_field='id', null=True)
    footprint_B = models.ForeignKey(Observation, on_delete=models.SET_NULL, db_column='footprint_B', related_name='footprint_B', to_field='id', null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'tile'


class TileObs(models.Model):
    id = models.BigAutoField(primary_key=True)
    tile = models.ForeignKey(Tile, on_delete=models.DO_NOTHING, db_column='tile_id', to_field='id')
    obs = models.ForeignKey(Observation, on_delete=models.DO_NOTHING, db_column='obs_id', to_field='id')

    class Meta:
        managed = False
        db_table = 'tile_obs'


class SurveyComponent(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=2048, blank=True, null=True)
    runs = ArrayField(models.TextField(), editable=False)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'survey_component'


class SurveyComponentRun(models.Model):
    id = models.BigAutoField(primary_key=True)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    sc = models.ForeignKey(SurveyComponent, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'survey_component_run'
        unique_together = (('run', 'sc'),)


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
        db_table = 'source_extraction_region'


class SourceExtractionRegionTile(models.Model):
    id = models.BigAutoField(primary_key=True)
    ser = models.ForeignKey(SourceExtractionRegion, on_delete=models.DO_NOTHING)
    tile = models.ForeignKey(Tile, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'source_extraction_region_tile'


# ------------------------------------------------------------------------------
# Project specific


if settings.PROJECT == 'DINGO':

    class DetectionNearestGAMA(models.Model):
        id = models.BigAutoField(primary_key=True)
        detection_id = models.ForeignKey('Detection', models.DO_NOTHING, db_column='detection_id', to_field='id')
        cata_id = models.BigIntegerField()

        class Meta:
            managed = False
            db_table = 'detection_nearest_gama'


if settings.PROJECT == 'WALLABY':

    class KinematicModel(models.Model):
        id = models.BigAutoField(primary_key=True)
        name = models.ForeignKey('Detection', models.DO_NOTHING)
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
            db_table = 'kinematic_model'
