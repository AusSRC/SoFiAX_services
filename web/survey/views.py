import io
import os
import tarfile
import urllib.parse
import logging

from urllib.request import pathname2url
from survey.utils.io import tarfile_write
from survey.utils.plot import product_summary_image
from survey.utils.components import get_survey_component, get_release_name
from survey.utils.forms import _add_tag, _add_comment
from survey.utils.views import handle_navigation, handle_next
from survey.models import Product, Instance, Detection, Run, Tag, TagDetection, \
    Comment, ExternalConflict, Task, FileTaskReturn, \
    KinematicModel, KinematicModel_3KIDNAS, WKAPP_Product, WRKP_Product
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
from django.utils.safestring import mark_safe


logging.basicConfig(level=logging.INFO)

PRODUCTS = ['mom0', 'mom1', 'mom2', 'cube', 'mask', 'chan', 'spec']
KINEMATIC_MODEL_3KIDNAS_PRODUCTS = ['bootstrapfits', 'diagnosticplot', 'diffcube', 'flag', 'modcube', 'procdata', 'pvmajordata', 'pvmajormod', 'pvminordata', 'pvminormod']


def logout_view(request):
    logout(request)
    url = settings.LOGOUT_URL + '?redirect_uri=' + urllib.parse.quote(f"https://{request.get_host()}/admin")
    return redirect(url)


def test(request):
    return HttpResponse('Authorized', status=200)


def summary_image(request):
    detection_id = request.GET.get('id', None)
    if detection_id is None:
        return HttpResponse('No summary image found', status=200)
    else:
        d = Detection.objects.get(id=detection_id)
        img = d.summary_image(size=(12, 9))
        return HttpResponse(img, status=200)


def instance_products(request):
    """Download products for all detections of an instance
    from the Admin portal.

    """
    instance_id = request.GET.get('id', None)
    if not instance_id:
        return HttpResponse('id does not exist.', status=400)
    try:
        instance_id = int(instance_id)
    except ValueError:
        return HttpResponse('id is not an integer.', status=400)

    # TODO(austin): refactor into function
    instance = Instance.objects.filter(id=instance_id).first()
    if not instance:
        return HttpResponse('instance not found.', status=404)

    detections = Detection.objects.filter(instance=instance)
    if not instance:
        return HttpResponse('no detections for this instance.', status=404)

    fh = io.BytesIO()
    with tarfile.open(fileobj=fh, mode='w:gz') as tar:
        for d in detections:
            name = f"{d.run.name}_{d.instance.id}_{d.name}"
            name = pathname2url(name.replace(' ', '_'))
            product = Product.objects.filter(detection=d).first()
            if product is None:
                return HttpResponse(
                    f'no products for detection {d.id}.',
                    status=404
                )
            folder = f'{d.name}'.replace(' ', '_')
            tarfile_write(tar, f'{folder}/{name}_mom0.fits', product.mom0)
            tarfile_write(tar, f'{folder}/{name}_mom1.fits', product.mom1)
            tarfile_write(tar, f'{folder}/{name}_mom2.fits', product.mom2)
            tarfile_write(tar, f'{folder}/{name}_cube.fits', product.cube)
            tarfile_write(tar, f'{folder}/{name}_mask.fits', product.mask)
            tarfile_write(tar, f'{folder}/{name}_chan.fits', product.chan)
            tarfile_write(tar, f'{folder}/{name}_spec.txt', product.spec)

    data = fh.getvalue()
    size = len(data)
    response = HttpResponse(data, content_type='application/x-tar')
    response['Content-Disposition'] = f'attachment; \
        filename={instance.run.name}_{instance.filename}.tar'
    response['Content-Length'] = size
    return response


def _read_in_chunks(filename, chunk_size=1024*64):
    with open(filename, 'rb') as infile:
        while True:
            chunk = infile.read(chunk_size)
            if chunk:
                yield chunk
            else:
                # The chunk was empty, which means we're at the end
                # of the file
                return


def task_file_download(request):
    task_id = request.GET.get('id', None)
    if not task_id:
        return HttpResponse('task id does not exist.', status=400)

    task = Task.objects.filter(id=task_id).first()
    if task.func not in ['download_accepted_sources', 'download_summaries']:
        return HttpResponse('No data.', status=404)

    if task.state != 'COMPLETED':
        return HttpResponse('Task failed or not ready', status=400)

    if request.user.username != task.user:
        return HttpResponse('Unauthorized', status=401)

    task = task.get_return()
    if isinstance(task, FileTaskReturn) is False:
        return HttpResponse('Not a File Task', status=400)

    filename = task.get_paths()[0]
    response = StreamingHttpResponse(streaming_content=_read_in_chunks(filename))
    response['Content-Disposition'] = f'attachment; filename={os.path.basename(filename)}'
    response['Content-Length'] = os.path.getsize(filename)
    return response


def detection_products(request):
    detect_id = request.GET.get('id', None)
    if not detect_id:
        return HttpResponse('id does not exist.', status=400)

    try:
        detect_id = int(detect_id)
    except ValueError:
        return HttpResponse('id is not an integer.', status=400)

    product_arg = request.GET.get('product', None)
    if product_arg is not None:
        product_arg = product_arg.lower()
        if product_arg not in PRODUCTS:
            return HttpResponse('not a valid detection product.', status=400)

    if product_arg is None:
        product = Product.objects.filter(detection=detect_id)\
            .select_related(
                'detection',
                'detection__instance',
                'detection__run')\
            .only(
                'detection__name',
                'detection__instance__id',
                'detection__run__name',
                'mom0',
                'mom1',
                'mom2',
                'cube',
                'mask',
                'chan',
                'spec',
                'plot')\
            .first()

        if not product:
            return HttpResponse('Products not found.', status=404)

        detection = product.detection
        name = f"{detection.run.name}_{detection.instance.id}_{detection.name}"
        name = pathname2url(name.replace(' ', '_'))

        fh = io.BytesIO()
        with tarfile.open(fileobj=fh, mode='w:gz') as tar:
            tarfile_write(tar, f'{name}_mom0.fits', product.mom0)
            tarfile_write(tar, f'{name}_mom1.fits', product.mom1)
            tarfile_write(tar, f'{name}_mom2.fits', product.mom2)
            tarfile_write(tar, f'{name}_cube.fits', product.cube)
            tarfile_write(tar, f'{name}_mask.fits', product.mask)
            tarfile_write(tar, f'{name}_chan.fits', product.chan)
            tarfile_write(tar, f'{name}_spec.txt', product.spec)
            tarfile_write(tar, f'{name}_plot.png', product.plot)

        data = fh.getvalue()
        size = len(data)

        response = HttpResponse(data, content_type='application/x-tar')
        response['Content-Disposition'] = f'attachment; filename={name}.tar.gz'
        response['Content-Length'] = size
        return response

    else:
        product = Product.objects.filter(detection=detect_id)\
            .select_related(
                'detection',
                'detection__instance',
                'detection__run')\
            .only(
                'detection__name',
                'detection__instance__id',
                'detection__run__name',
                product_arg)
        if not product:
            return HttpResponse('products not found.', status=404)

        detect_name = product[0].detection.name
        run_name = product[0].detection.run.name
        inst_name = product[0].detection.instance.id
        name = f"{run_name}_{inst_name}_{detect_name}"
        name = pathname2url(name.replace(' ', '_'))

        data = getattr(product[0], product_arg)
        size = len(data)

        content_type = 'image/fits'
        ext = "fits"
        if product_arg == "spec":
            content_type = "text/plain"
            ext = "txt"

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; \
            filename={name}_{product_arg}.{ext}'
        response['Content-Length'] = size
        return response


def run_products(request):
    """Download products for all detections of a run
    from the Admin portal.

    """
    run_id = request.GET.get('id', None)
    if not run_id:
        return HttpResponse('id does not exist.', status=400)

    try:
        run_id = int(run_id)
    except ValueError:
        return HttpResponse('id is not an integer.', status=400)

    run = Run.objects.filter(id=run_id).first()
    if not run:
        return HttpResponse('run not found.', status=404)

    detections = Detection.objects.filter(run=run)
    if detections is None:
        return HttpResponse('no detections for this run.', status=404)

    fh = io.BytesIO()
    with tarfile.open(fileobj=fh, mode='w:gz') as tar:
        for d in detections:
            name = f"{d.run.name}_{d.instance.id}_{d.name}"
            name = pathname2url(name.replace(' ', '_'))
            product = Product.objects.filter(detection=d).first()
            if product is None:
                return HttpResponse(
                    f'no products for detection {d.id}.',
                    status=404
                )
            folder = f'{d.name}'.replace(' ', '_')
            tarfile_write(tar, f'{folder}/{name}_mom0.fits', product.mom0)
            tarfile_write(tar, f'{folder}/{name}_mom1.fits', product.mom1)
            tarfile_write(tar, f'{folder}/{name}_mom2.fits', product.mom2)
            tarfile_write(tar, f'{folder}/{name}_cube.fits', product.cube)
            tarfile_write(tar, f'{folder}/{name}_mask.fits', product.mask)
            tarfile_write(tar, f'{folder}/{name}_chan.fits', product.chan)
            tarfile_write(tar, f'{folder}/{name}_spec.txt', product.spec)

    data = fh.getvalue()
    size = len(data)

    response = HttpResponse(data, content_type='application/x-tar')
    response['Content-Disposition'] = f'attachment; \
        filename={run.id}_{run.name}_products.tar'
    response['Content-Length'] = size
    return response


def _build_detection(detection):
    det = \
        f'<TR>\n' \
        f'<TD>{detection.name}</TD>\n' \
        f'<TD>{detection.id}</TD>\n' \
        f'<TD>{detection.x}</TD>\n' \
        f'<TD>{detection.y}</TD>\n' \
        f'<TD>{detection.z}</TD>\n' \
        f'<TD>{detection.x_min}</TD>\n' \
        f'<TD>{detection.x_max}</TD>\n' \
        f'<TD>{detection.y_min}</TD>\n' \
        f'<TD>{detection.y_max}</TD>\n' \
        f'<TD>{detection.z_min}</TD>\n' \
        f'<TD>{detection.z_max}</TD>\n' \
        f'<TD>{detection.n_pix}</TD>\n' \
        f'<TD>{detection.f_min}</TD>\n' \
        f'<TD>{detection.f_max}</TD>\n' \
        f'<TD>{detection.f_sum}</TD>\n' \
        f'<TD>{"" if detection.rel is None else detection.rel}</TD>\n' \
        f'<TD>{detection.flag}</TD>\n' \
        f'<TD>{detection.rms}</TD>\n' \
        f'<TD>{detection.w20}</TD>\n' \
        f'<TD>{detection.w50}</TD>\n' \
        f'<TD>{detection.ell_maj}</TD>\n' \
        f'<TD>{detection.ell_min}</TD>\n' \
        f'<TD>{detection.ell_pa}</TD>\n' \
        f'<TD>{detection.ell3s_maj}</TD>\n' \
        f'<TD>{detection.ell3s_min}</TD>\n' \
        f'<TD>{detection.ell3s_pa}</TD>\n' \
        f'<TD>{"" if detection.kin_pa is None else detection.kin_pa}</TD>\n' \
        f'<TD>{detection.err_x}</TD>\n' \
        f'<TD>{detection.err_y}</TD>\n' \
        f'<TD>{detection.err_z}</TD>\n' \
        f'<TD>{detection.err_f_sum}</TD>\n' \
        f'<TD>{"" if detection.ra is None else detection.ra}</TD>\n' \
        f'<TD>{"" if detection.dec is None else detection.dec}</TD>\n' \
        f'<TD>{"" if detection.freq is None else detection.freq}</TD>\n' \
        f'<TD>{"" if detection.l is None else detection.l}</TD>\n' \
        f'<TD>{"" if detection.b is None else detection.b}</TD>\n' \
        f'<TD>{"" if detection.v_rad is None else detection.v_rad}</TD>\n' \
        f'<TD>{"" if detection.v_opt is None else detection.v_opt}</TD>\n' \
        f'<TD>{"" if detection.v_app is None else detection.v_app}</TD>\n' \
        f'</TR>\n'
    return det


def _build_catalog(detections, date, version):
    cat = \
        f'<?xml version="1.0" ?>\n' \
        f'<VOTABLE version="1.3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
        f'xmlns="http://www.ivoa.net/xml/VOTable/v1.3">\n' \
        f'<RESOURCE>\n' \
        f'<DESCRIPTION>Source catalogue created by the Source Finding Application(SoFiA)</DESCRIPTION>\n' \
        f'<PARAM name="Creator" datatype="char" arraysize="*" value="{"" if version is None else version}"' \
        f' ucd="meta.id;meta.software"/>\n' \
        f'<PARAM name="Time" datatype="char" arraysize="*" value="{date}" ' \
        f'ucd="time.creation"/>\n' \
        f'<TABLE ID="SoFiA_source_catalogue" name="SoFiA source catalogue">\n' \
        f'<FIELD arraysize="32" datatype="char" name="name" unit="" ucd="meta.id"/>\n' \
        f'<FIELD datatype="long" name="id" unit="" ucd="meta.id"/>\n' \
        f'<FIELD datatype="double" name="x" unit="pix" ucd="pos.cartesian.x"/>\n' \
        f'<FIELD datatype="double" name="y" unit="pix" ucd="pos.cartesian.y"/>\n' \
        f'<FIELD datatype="double" name="z" unit="pix" ucd="pos.cartesian.z"/>\n' \
        f'<FIELD datatype="long" name="x_min" unit="pix" ucd="pos.cartesian.x;stat.min"/>\n' \
        f'<FIELD datatype="long" name="x_max" unit="pix" ucd="pos.cartesian.x;stat.max"/>\n' \
        f'<FIELD datatype="long" name="y_min" unit="pix" ucd="pos.cartesian.y;stat.min"/>\n' \
        f'<FIELD datatype="long" name="y_max" unit="pix" ucd="pos.cartesian.y;stat.max"/>\n' \
        f'<FIELD datatype="long" name="z_min" unit="pix" ucd="pos.cartesian.z;stat.min"/>\n' \
        f'<FIELD datatype="long" name="z_max" unit="pix" ucd="pos.cartesian.z;stat.max"/>\n' \
        f'<FIELD datatype="long" name="n_pix" unit="" ucd="meta.number;instr.pixel"/>\n' \
        f'<FIELD datatype="double" name="f_min" unit="Jy/beam" ucd="phot.flux.density;stat.min"/>\n' \
        f'<FIELD datatype="double" name="f_max" unit="Jy/beam" ucd="phot.flux.density;stat.max"/>\n' \
        f'<FIELD datatype="double" name="f_sum" unit="Jy*Hz" ucd="phot.flux"/>\n' \
        f'<FIELD datatype="double" name="rel" unit="" ucd="stat.probability"/>\n' \
        f'<FIELD datatype="long" name="flag" unit="" ucd="meta.code.qual"/>\n' \
        f'<FIELD datatype="double" name="rms" unit="Jy/beam" ucd="instr.det.noise"/>\n' \
        f'<FIELD datatype="double" name="w20" unit="Hz" ucd="spect.line.width"/>\n' \
        f'<FIELD datatype="double" name="w50" unit="Hz" ucd="spect.line.width"/>\n' \
        f'<FIELD datatype="double" name="ell_maj" unit="pix" ucd="phys.angSize"/>\n' \
        f'<FIELD datatype="double" name="ell_min" unit="pix" ucd="phys.angSize"/>\n' \
        f'<FIELD datatype="double" name="ell_pa" unit="deg" ucd="pos.posAng"/>\n' \
        f'<FIELD datatype="double" name="ell3s_maj" unit="pix" ucd="phys.angSize"/>\n' \
        f'<FIELD datatype="double" name="ell3s_min" unit="pix" ucd="phys.angSize"/>\n' \
        f'<FIELD datatype="double" name="ell3s_pa" unit="deg" ucd="pos.posAng"/>\n' \
        f'<FIELD datatype="double" name="kin_pa" unit="deg" ucd="pos.posAng"/>\n' \
        f'<FIELD datatype="double" name="err_x" unit="pix" ucd="stat.error;pos.cartesian.x"/>\n' \
        f'<FIELD datatype="double" name="err_y" unit="pix" ucd="stat.error;pos.cartesian.y"/>\n' \
        f'<FIELD datatype="double" name="err_z" unit="pix" ucd="stat.error;pos.cartesian.z"/>\n' \
        f'<FIELD datatype="double" name="err_f_sum" unit="Jy*Hz" ucd="stat.error;phot.flux"/>\n' \
        f'<FIELD datatype="double" name="ra" unit="deg" ucd="pos.eq.ra"/>\n' \
        f'<FIELD datatype="double" name="dec" unit="deg" ucd="pos.eq.dec"/>\n' \
        f'<FIELD datatype="double" name="freq" unit="Hz" ucd="em.freq"/>\n' \
        f'<FIELD datatype="double" name="l" unit="deg" ucd="pos.galactic.lon"/>\n'\
        f'<FIELD datatype="double" name="b" unit="deg" ucd="pos.galactic.lat"/>\n' \
        f'<FIELD datatype="double" name="v_rad" unit="m/s" ucd="spect.dopplerVeloc.radio"/>\n' \
        f'<FIELD datatype="double" name="v_opt" unit="m/s" ucd="spect.dopplerVeloc.opt"/>\n' \
        f'<FIELD datatype="double" name="v_app" unit="m/s" ucd="spect.dopplerVeloc"/>\n' \
        f'<DATA>\n' \
        f'<TABLEDATA>\n' \
        f'{"".join([_build_detection(detection) for detection in detections])}' \
        f'</TABLEDATA>\n' \
        f'</DATA>\n' \
        f'</TABLE>\n' \
        f'</RESOURCE>\n' \
        f'</VOTABLE>\n'
    return cat


def run_catalog(request):
    run_id = request.GET.get('id', None)
    if not run_id:
        return HttpResponse('id does not exist.', status=400)

    try:
        run_id = int(run_id)
    except ValueError:
        return HttpResponse('id is not an integer.', status=400)

    detections = Detection.objects.filter(run=run_id)
    if not detections:
        return HttpResponse('no detections found.', status=404)

    instance = Instance.objects.filter(run=run_id)\
        .order_by('-run_date')\
        .first()
    if not instance:
        return HttpResponse('no instance found.', status=404)

    cat = _build_catalog(detections, instance.run_date, instance.version)

    name = f'{run_id}_{detections[0].run.name}.xml'

    response = HttpResponse(cat, content_type='text/xml')
    response['Content-Disposition'] = f'attachment; filename={name}'
    response['Content-Length'] = len(cat)
    return response


# TODO: require superuser status
def manual_inspection_detection_view(request):
    # Handle GET request
    if request.method == 'GET':
        run_id = request.GET.get('run_id', None)
        if not run_id:
            raise Exception('Run not selected or does not exist.')
        try:
            run_id = int(run_id)
        except ValueError:
            return HttpResponse('Run id is not an integer.', status=400)

        run = Run.objects.get(id=int(run_id))
        queryset = Detection.objects.filter(
            run=run,
            accepted=False,
            source_name__isnull=True,
            n_pix__gte=300,
            rel__gte=0.7
        )

        if len(queryset) == 0:
            messages.info(request, "All detections for this run have been resolved")
            return HttpResponseRedirect('/admin/survey/run')
        detection_id = request.GET.get('detection_id', queryset[0].id)
        detection = Detection.objects.get(id=detection_id)
        idx = list(queryset).index(detection)

        # Show image
        product = Product.objects.get(detection=detection)
        img_src = product_summary_image(product, size=(12, 9))

        properties = {
            'RA': round(detection.ra, 4),
            'Dec': round(detection.dec, 4),
            'freq [MHz]': round(detection.freq / 10**6, 2),
            'v_opt': round(299792.458 * (1.42040575e+9 / detection.freq - 1.0), 2),
            'f_sum': round(detection.f_sum, 2),
            'rel': round(detection.rel, 2),
            'rms [mJy]': round(detection.rms * 10**3, 2),
            'snr': round(detection.f_sum / detection.err_f_sum, 2),
        }

        links = {
            "NED": f"https://ned.ipac.caltech.edu/cgi-bin/objsearch?search_type=Near+Position+Search&in_csys=Equatorial&in_equinox=J2000.0&lon={round(detection.ra, 5)}d&lat={round(detection.dec, 5)}d&radius=0.5",
            "LS-DR10": f"https://www.legacysurvey.org/viewer/jpeg-cutout?layer=ls-dr10&ra={round(detection.ra, 5)}&dec={round(detection.dec, 5)}&pixscale=0.262&size=768"
        }

        matches = {}
        if settings.PROJECT == 'DINGO':
            gama = detection.detectionnearestgama_set.all()
            matches['GAMA'] = ", ".join([str(g.cata_id) for g in gama])

        # Form content
        params = {
            'title': detection.name,
            'subheading': detection.description_string(),
            'subsubheading': f'{idx + 1}/{len(queryset)} detections to resolve.',
            'properties': properties,
            'run_id': run_id,
            'detection_id': detection.id,
            'image': mark_safe(img_src),
            'tags': Tag.objects.all(),
            'links': links,
            'matches': matches
        }

        return render(request, 'admin/form_inspect_detection.html', params)

    # Handle POST
    elif request.method == 'POST':
        body = dict(request.POST)
        run = Run.objects.get(id=int(body['run_id'][0]))
        detection = Detection.objects.get(id=int(body['detection_id'][0]))
        queryset = Detection.objects.filter(
            run=run,
            accepted=False,
            source_name__isnull=True,
            n_pix__gte=300,
            rel__gte=0.7
        )
        idx = list(queryset).index(detection)
        url_base = reverse('inspect_detection')
        url_params = f'run_id={run.id}&detection_id='

        if 'Accept' in body['action']:
            logging.info(f'Marking detection {detection.name} as an accepted detection.')
            logging.debug(detection.__dict__)
            detection.accepted = True
            detection.save()

            tag_select = request.POST['tag_select']
            tag_create = str(request.POST['tag_create'])
            if (tag_select != 'None') or (tag_create != ''):
                _add_tag(request, detection)
            _add_comment(request, detection)
            url = handle_next(request, queryset, idx, url_base, url_params)
            return HttpResponseRedirect(url)

        url = handle_navigation(request, queryset, idx, url_base, url_params)
        if not url:
            messages.warning(request, "Selected action that should not exist.")
            url = f"{url_base}?{url_params}{queryset[idx].id}"
        return HttpResponseRedirect(url)
    else:
        messages.warning(request, "Error, returning to run.")
        return HttpResponseRedirect('/admin/survey/run')


# TODO: require superuser status
def external_conflict_view(request):
    if request.method == 'GET':
        run_id = request.GET.get('run_id', None)
        if not run_id:
            raise Exception('Run not selected or does not exist.')
        try:
            run_id = int(run_id)
        except ValueError:
            return HttpResponse('Run id is not an integer.', status=400)

        run = Run.objects.get(id=run_id)
        conflicts = ExternalConflict.objects.filter(
            detection_id__in=[d.id for d in Detection.objects.filter(run=run)])
        if len(conflicts) == 0:
            messages.info(request, "All external conflicts for this run have been resolved")
            return HttpResponseRedirect('/admin/survey/run')

        ex_c_id = int(request.GET.get('external_conflict_id', conflicts[0].id))
        ex_c = ExternalConflict.objects.get(id=ex_c_id)
        idx = list(conflicts).index(ex_c)

        # Show image
        product = Product.objects.get(detection=ex_c.detection)
        img_src = product_summary_image(product, size=(6, 4))
        description = ''
        description += ', '.join([td.tag.name for td in TagDetection.objects.filter(detection=ex_c.detection)])
        description += ', '.join([c.comment for c in Comment.objects.filter(detection=ex_c.detection)])
        if description == '':
            description = "No tags or comments"
        properties = {
            'x': round(ex_c.detection.x, 2),
            'y': round(ex_c.detection.y, 2),
            'z': round(ex_c.detection.z, 2),
            'f_sum': round(ex_c.detection.f_sum, 2),
            'ell_maj': round(ex_c.detection.ell_maj, 2),
            'ell_min': round(ex_c.detection.ell_min, 2),
            'w20': round(ex_c.detection.w20, 2),
            'w50': round(ex_c.detection.w50, 2)
        }

        # Show conflict
        c_product = Product.objects.get(detection=ex_c.conflict_detection)
        c_img_src = product_summary_image(c_product, size=(6, 4))
        c_properties = {
            'x': round(ex_c.conflict_detection.x, 2),
            'y': round(ex_c.conflict_detection.y, 2),
            'z': round(ex_c.conflict_detection.z, 2),
            'f_sum': round(ex_c.conflict_detection.f_sum, 2),
            'ell_maj': round(ex_c.conflict_detection.ell_maj, 2),
            'ell_min': round(ex_c.conflict_detection.ell_min, 2),
            'w20': round(ex_c.conflict_detection.w20, 2),
            'w50': round(ex_c.conflict_detection.w50, 2)
        }
        # Check same survey component for additional functionality
        detection_survey_component = get_survey_component(ex_c.detection)
        conflict_survey_component = get_survey_component(ex_c.conflict_detection)
        same_survey_component = detection_survey_component == conflict_survey_component

        # Form content
        params = {
            'title': ex_c.detection.name,
            'subheading': f'{idx + 1}/{len(conflicts)} conflicts to resolve.',
            'name': ex_c.detection.name,
            'description': ex_c.detection.description_string(),
            'image': mark_safe(img_src),
            'properties': properties,
            'conflict_name': ex_c.conflict_detection.source_name,
            'conflict_description': ex_c.conflict_detection.description_string(),
            'conflict_image': mark_safe(c_img_src),
            'conflict_properties': c_properties,
            'run_id': run_id,
            'external_conflict_id': ex_c.id,
            'tags': Tag.objects.all(),
            'same_survey_component': same_survey_component,
        }
        logging.info(f'External conflict {ex_c.detection} [{detection_survey_component}] with {ex_c.conflict_detection} [{conflict_survey_component}]')
        return render(request, 'admin/form_external_conflict.html', params)

    # Handle POST
    elif request.method == 'POST':
        body = dict(request.POST)
        run = Run.objects.get(id=int(body['run_id'][0]))
        logging.info(f'External conflict resolution for run {run.name}')
        ex_c = ExternalConflict.objects.get(id=int(body['external_conflict_id'][0]))
        conflicts = ExternalConflict.objects.filter(
            detection_id__in=[d.id for d in Detection.objects.filter(run=run)]
        )
        idx = list(conflicts).index(ex_c)

        if 'Add tags and comments' in body['action']:
            with transaction.atomic():
                # Tag both detections in conflict
                _add_tag(request, ex_c.detection)
                _add_comment(request, ex_c.detection)
                _add_tag(request, ex_c.conflict_detection, tag_select_input='tag_select_conflict', tag_create_input='tag_create_conflict')
                _add_comment(request, ex_c.conflict_detection, comment_input='comment_conflict')
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={ex_c.id}"
            return HttpResponseRedirect(url)

        if 'Keep new source name' in body['action']:
            with transaction.atomic():
                # Check against existing sources
                new_name = get_release_name(ex_c.detection.name)
                if new_name in [d.source_name for d in Detection.objects.filter(accepted=True, source_name__isnull=False)]:
                    messages.error(request, f"Existing source with name {new_name} exists so cannot accept this detection.")
                    url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[idx].id}"
                    return HttpResponseRedirect(url)
                # Accept new name as an official (and separate) source
                logging.info(f'Adding official name {new_name} to detection {ex_c.detection.name}')
                ex_c.detection.source_name = new_name
                ex_c.detection.save()
                ex_c.delete()
            url = handle_next(request, conflicts, idx, reverse('external_conflict'), f'run_id={run.id}&external_conflict_id=')
            return HttpResponseRedirect(url)

        if 'Delete conflict' in body['action']:
            with transaction.atomic():
                # Remove any conflicts that may have previously been accepted for this detection
                logging.info(f'De-selecting detection {ex_c.detection}')
                ex_c.detection.source_name = None
                ex_c.detection.accepted = False
                ex_c.detection.save()

                # Remove external conflicts
                logging.info(f'Deleting external conflicts for detection {ex_c.detection}')
                for c in ExternalConflict.objects.filter(detection=ex_c.detection):
                    c.delete()
                # NOTE: issue with indexing here if multiple conflicts have been deleted
                url = handle_next(request, conflicts, idx, reverse('external_conflict'), f'run_id={run.id}&external_conflict_id=')
            return HttpResponseRedirect(url)

        if 'Copy old source name' in body['action']:
            with transaction.atomic():
                logging.info(f'Adding existing source name {ex_c.conflict_detection.source_name} to current detection {ex_c.detection.name}.')
                ex_c.detection.source_name = ex_c.conflict_detection.source_name
                ex_c.detection.save()
                ex_c.delete()
            url = handle_next(request, conflicts, idx, reverse('external_conflict'), f'run_id={run.id}&external_conflict_id=')
            return HttpResponseRedirect(url)

        if 'Replace detection in source' in body['action']:
            source_name = ex_c.conflict_detection.source_name
            logging.info(f'Replacing detection {ex_c.conflict_detection} with {ex_c.detection} in source {source_name}.')
            with transaction.atomic():
                ex_c.detection.source_name = source_name
                ex_c.detection.save()
                ex_c.conflict_detection.source_name = None
                ex_c.conflict_detection.save()

                # Remove release tag detection entry for replaced detection
                remove_tagdetections = TagDetection.objects.filter(detection=ex_c.conflict_detection, tag__type='release')
                for td in remove_tagdetections:
                    logging.info(f'Removing tag detection objects: {td.id} [tag: {td.tag_id}, detection: {td.detection_id}]')
                    td.delete()

                ex_c.delete()
            url = handle_next(request, conflicts, idx, reverse('external_conflict'), f'run_id={run.id}&external_conflict_id=')
            return HttpResponseRedirect(url)

        url = handle_navigation(request, conflicts, idx, reverse('external_conflict'), f'run_id={run.id}&external_conflict_id=')
        if not url:
            messages.warning(request, "Selected action that should not exist.")
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[idx].id}"
        return HttpResponseRedirect(url)
    else:
        messages.warning(request, "Error, returning to run.")
        return HttpResponseRedirect('/admin/survey/run')


def wrkp_products(request):
    kinematic_model_3kidnas_id = request.GET.get('id', None)
    if not kinematic_model_3kidnas_id:
        return HttpResponse('id does not exist.', status=400)

    try:
        kinematic_model_3kidnas_id = int(kinematic_model_3kidnas_id)
    except ValueError:
        return HttpResponse('id is not an integer.', status=400)

    # Get a specific product from the wkrp_product table
    product_arg = request.GET.get('wrkp_product', None)
    if product_arg is not None:
        product_arg = product_arg.lower()
        if product_arg not in KINEMATIC_MODEL_3KIDNAS_PRODUCTS:
            return HttpResponse('not a valid kinematic_model_3kidnas wrkp_product.', status=400)

    # Query model and products
    kinematic_model = KinematicModel_3KIDNAS.objects.get(id=kinematic_model_3kidnas_id)
    product = WRKP_Product.objects.get(kinematic_model_3kidnas=kinematic_model)
    run = Run.objects.get(id=kinematic_model.detection.run_id)
    name = f"{run.name}_{kinematic_model.detection.name}"
    name = pathname2url(name.replace(' ', '_'))
    if not product:
        return HttpResponse('Products not found.', status=404)

    if product_arg is None:
        fh = io.BytesIO()
        with tarfile.open(fileobj=fh, mode='w:gz') as tar:
            tarfile_write(tar, f'{name}_bootstrapfits.fits', product.bootstrapfits)
            tarfile_write(tar, f'{name}_diagnosticplot.fits', product.diagnosticplot)
            tarfile_write(tar, f'{name}_diffcube.fits', product.diffcube)
            tarfile_write(tar, f'{name}_flag.fits', product.flag)
            tarfile_write(tar, f'{name}_modcube.fits', product.modcube)
            tarfile_write(tar, f'{name}_procdata.fits', product.procdata)
            tarfile_write(tar, f'{name}_pvmajordata.fits', product.pvmajordata)
            tarfile_write(tar, f'{name}_pvmajormod.fits', product.pvmajormod)
            tarfile_write(tar, f'{name}_pvminordata.fits', product.pvminordata)
            tarfile_write(tar, f'{name}_pvminormo.fits', product.pvminormod)

        data = fh.getvalue()
        size = len(data)

        response = HttpResponse(data, content_type='application/x-tar')
        response['Content-Disposition'] = f'attachment; filename={name}.tar.gz'
        response['Content-Length'] = size
        return response
    else:
        data = getattr(product, product_arg)
        size = len(data)

        content_type = 'image/fits'
        ext = "fits"
        if product_arg == "spec":
            content_type = "text/plain"
            ext = "txt"

        response = HttpResponse(data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; \
            filename={name}_{product_arg}.{ext}'
        response['Content-Length'] = size
        return response
