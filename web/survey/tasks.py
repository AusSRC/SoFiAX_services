import uuid
import tarfile
import logging
from datetime import datetime

from astropy.table import Table, MaskedColumn
from astropy.io.votable import from_table, writeto

from survey.models import Product, Detection, Run, FileTaskReturn
from survey.utils.task import task
from survey.utils.io import tarfile_write
from urllib.request import pathname2url


# (name, dtype, unit, ucd) for each column of the accepted detections catalogue
CATALOG_COLUMNS = [
    ('id', 'i8', None, 'meta.id'),
    ('run', 'U', None, 'meta.id;meta.dataset'),
    ('name', 'U', None, 'meta.id'),
    ('source_name', 'U', None, 'meta.id;meta.main'),
    ('x', 'f8', 'pix', 'pos.cartesian.x'),
    ('y', 'f8', 'pix', 'pos.cartesian.y'),
    ('z', 'f8', 'pix', 'pos.cartesian.z'),
    ('x_min', 'i8', 'pix', 'pos.cartesian.x;stat.min'),
    ('x_max', 'i8', 'pix', 'pos.cartesian.x;stat.max'),
    ('y_min', 'i8', 'pix', 'pos.cartesian.y;stat.min'),
    ('y_max', 'i8', 'pix', 'pos.cartesian.y;stat.max'),
    ('z_min', 'i8', 'pix', 'pos.cartesian.z;stat.min'),
    ('z_max', 'i8', 'pix', 'pos.cartesian.z;stat.max'),
    ('n_pix', 'i8', None, 'meta.number;instr.pixel'),
    ('f_min', 'f8', 'Jy/beam', 'phot.flux.density;stat.min'),
    ('f_max', 'f8', 'Jy/beam', 'phot.flux.density;stat.max'),
    ('f_sum', 'f8', 'Jy*Hz', 'phot.flux'),
    ('rel', 'f8', None, 'stat.probability'),
    ('flag', 'i8', None, 'meta.code.qual'),
    ('rms', 'f8', 'Jy/beam', 'instr.det.noise'),
    ('w20', 'f8', 'Hz', 'spect.line.width'),
    ('w50', 'f8', 'Hz', 'spect.line.width'),
    ('wm50', 'f8', 'Hz', 'spect.line.width'),
    ('ell_maj', 'f8', 'pix', 'phys.angSize'),
    ('ell_min', 'f8', 'pix', 'phys.angSize'),
    ('ell_pa', 'f8', 'deg', 'pos.posAng'),
    ('ell3s_maj', 'f8', 'pix', 'phys.angSize'),
    ('ell3s_min', 'f8', 'pix', 'phys.angSize'),
    ('ell3s_pa', 'f8', 'deg', 'pos.posAng'),
    ('kin_pa', 'f8', 'deg', 'pos.posAng'),
    ('err_x', 'f8', 'pix', 'stat.error;pos.cartesian.x'),
    ('err_y', 'f8', 'pix', 'stat.error;pos.cartesian.y'),
    ('err_z', 'f8', 'pix', 'stat.error;pos.cartesian.z'),
    ('err_f_sum', 'f8', 'Jy*Hz', 'stat.error;phot.flux'),
    ('ra', 'f8', 'deg', 'pos.eq.ra'),
    ('dec', 'f8', 'deg', 'pos.eq.dec'),
    ('freq', 'f8', 'Hz', 'em.freq'),
    ('l', 'f8', 'deg', 'pos.galactic.lon'),
    ('b', 'f8', 'deg', 'pos.galactic.lat'),
    ('v_rad', 'f8', 'm/s', 'spect.dopplerVeloc.radio'),
    ('v_opt', 'f8', 'm/s', 'spect.dopplerVeloc.opt'),
    ('v_app', 'f8', 'm/s', 'spect.dopplerVeloc'),
    ('x_peak', 'i8', 'pix', 'pos.cartesian.x;phot.flux;stat.max'),
    ('y_peak', 'i8', 'pix', 'pos.cartesian.y;phot.flux;stat.max'),
    ('z_peak', 'i8', 'pix', 'pos.cartesian.z;phot.flux;stat.max'),
    ('ra_peak', 'f8', 'deg', 'pos.eq.ra;phot.flux;stat.max'),
    ('dec_peak', 'f8', 'deg', 'pos.eq.dec;phot.flux;stat.max'),
    ('freq_peak', 'f8', 'Hz', 'em.freq;phot.flux;stat.max'),
]


def _catalog_value(detection, name):
    if name == 'run':
        return detection.run.name
    value = getattr(detection, name)
    if value is None:
        return None
    # PostgresDecimalField values are Decimal, which astropy cannot serialise
    return float(value) if not isinstance(value, (int, str)) else value


@task()
def download_accepted_sources(request, queryset):
    ids = [d.id for d in queryset]
    products = Product.objects.filter(detection_id__in=ids)

    uuid_id = str(uuid.uuid4())
    uuid_filename = f"/tmp/{uuid_id}.tar.gz"

    with tarfile.open(uuid_filename, mode='w:gz') as tar:
        for product in products:
            detection = product.detection
            name = f"{detection.run.name}_{detection.instance.id}_{detection.name}"
            name = pathname2url(name.replace(' ', '_'))
            folder = f'{detection.run.name}'.replace(' ', '_')

            tarfile_write(tar, f'{folder}/{name}_mom0.fits', product.mom0)
            tarfile_write(tar, f'{folder}/{name}_mom1.fits', product.mom1)
            tarfile_write(tar, f'{folder}/{name}_mom2.fits', product.mom2)
            tarfile_write(tar, f'{folder}/{name}_cube.fits', product.cube)
            tarfile_write(tar, f'{folder}/{name}_mask.fits', product.mask)
            tarfile_write(tar, f'{folder}/{name}_chan.fits', product.chan)
            tarfile_write(tar, f'{folder}/{name}_spec.txt', product.spec)
            if product.pv is not None:
                tarfile_write(tar, f'{folder}/{name}_pv.fits', product.pv)
            try:
                tarfile_write(tar, f'{folder}/{name}_summary.png', detection.summary_image(size=(8, 6), binary_image=True))
            except Exception as e:
                logging.error(f'Failed to write summary figure for detection {detection}: {e}')

    return FileTaskReturn([uuid_filename])


def _catalog_run_ids(request, queryset):
    """Runs to include in the catalogue: the run the admin page is filtered to (?run=<id>),
    otherwise the runs of the selected detections.
    """
    run_id = request.GET.get('run')
    if run_id is not None:
        try:
            return [int(run_id)]
        except ValueError:
            raise ValueError(f'run {run_id} is not an integer')
    return list(queryset.values_list('run_id', flat=True).distinct())


@task()
def download_accepted_sources_catalog(request, queryset):
    """Write all accepted detections of the current run to a VOTable (XML) catalogue.
    """
    run_ids = _catalog_run_ids(request, queryset)
    if not run_ids:
        raise ValueError('No run found for the catalogue')

    detections = list(
        Detection.objects.filter(run_id__in=run_ids, accepted=True).select_related('run').order_by('id')
    )

    table = Table()
    for name, dtype, unit, ucd in CATALOG_COLUMNS:
        values = [_catalog_value(d, name) for d in detections]
        mask = [v is None for v in values]
        if dtype == 'U':
            data = ['' if v is None else v for v in values]
        else:
            data = [0 if v is None else v for v in values]
        table[name] = MaskedColumn(data, name=name, dtype=dtype if dtype != 'U' else str,
                                   unit=unit, mask=mask, meta={'ucd': ucd})

    votable = from_table(table)
    resource = votable.resources[0]
    resource.description = 'Accepted detections catalogue created by SoFiAX services'
    vo_table = resource.tables[0]
    vo_table.ID = 'accepted_detections'
    vo_table.name = 'Accepted detections'

    run_names = '_'.join(Run.objects.filter(id__in=run_ids).order_by('id').values_list('name', flat=True))
    run_names = pathname2url(run_names.replace(' ', '_'))
    uuid_id = str(uuid.uuid4())
    uuid_filename = f"/tmp/{uuid_id}_{run_names}_accepted_detections_{datetime.now():%Y%m%d}.xml"
    writeto(votable, uuid_filename)

    return FileTaskReturn([uuid_filename])


def download_summaries_for_run(request, queryset):
    uuid_id = str(uuid.uuid4())
    uuid_filename = f"/tmp/{uuid_id}.tar.gz"

    with tarfile.open(uuid_filename, mode='w:gz') as tar:
        for detection in queryset[0].detection_set.all():
            name = f"{detection.run.name}_{detection.instance.id}_{detection.name}"
            name = pathname2url(name.replace(' ', '_'))
            folder = f'{detection.run.name}'.replace(' ', '_')

            # No image for HTML summary plots
            image = detection.summary_image(size=(8, 6), binary_image=True)
            if image is not None:
                tarfile_write(tar, f'{folder}/{name}_summary.png', image)

    return FileTaskReturn([uuid_filename])
