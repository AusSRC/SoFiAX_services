import io
import os
import json
import tarfile
import urllib.parse
import logging

from urllib.request import pathname2url
from survey.utils.io import tarfile_write
from survey.utils.plot import product_summary_image
from survey.utils.components import get_survey_component, get_release_name
from survey.utils.forms import add_tag, add_comment
from survey.decorators import basic_auth
from survey.models import Product, Instance, Detection, Run, Tag, TagSourceDetection, Source, \
    SourceDetection, Comment, ExternalConflict, Task, FileTaskReturn
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
from django.utils.safestring import mark_safe


logging.basicConfig(level=logging.INFO)
PRODUCTS = ['mom0', 'mom1', 'mom2',
            'cube', 'mask', 'chan', 'spec']


def logout_view(request):
    logout(request)
    url = settings.LOGOUT_URL + '?redirect_uri=' + urllib.parse.quote(f"https://{request.get_host()}/admin")
    return redirect(url)


@basic_auth
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


@basic_auth
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


@basic_auth
def task_file_download(request):
    task_id = request.GET.get('id', None)
    if not task_id:
        return HttpResponse('task id does not exist.', status=400)

    task = Task.objects.filter(id=task_id).first()
    if task.func != 'download_accepted_sources':
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


@basic_auth
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
                'spec')\
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


@basic_auth
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


@basic_auth
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
def inspect_detection_view(request):
    # Handle GET request
    if request.method == 'GET':
        run_id = request.GET.get('run_id', None)
        if not run_id:
            raise Exception('Run not selected or does not exist.')
        try:
            run_id = int(run_id)
        except ValueError:
            return HttpResponse('Run id is not an integer.', status=400)
        run = Run.objects.get(id=run_id)
        detections_to_resolve = Detection.objects.filter(
            run=run,
            n_pix__gte=300,
            rel__gte=0.7
        ).exclude(
            id__in=[sd.detection_id for sd in SourceDetection.objects.all()]
        )
        if len(detections_to_resolve) == 0:
            messages.info(request, "All detections for this run have been resolved")
            return HttpResponseRedirect('/admin/survey/run')

        detection_id = request.GET.get('detection_id', None)
        if detection_id is None:
            # Should only be the case when entering the manual inspection view
            detection = detections_to_resolve[0]
        else:
            detection = Detection.objects.get(id=detection_id)
        current_idx = list(detections_to_resolve).index(detection)

        # Show image
        product = Product.objects.get(detection=detection)
        img_src = product_summary_image(product, size=(12, 9))
        sd = SourceDetection.objects.filter(detection=detection)
        description = ''
        if sd:
            tag_sd = TagSourceDetection.objects.filter(source_detection=sd[0])
            if tag_sd:
                tags = Tag.objects.filter(id__in=[tsd.tag_id for tsd in tag_sd])
                description += ', '.join([t.name for t in tags])
        description += ', '.join([c.comment for c in Comment.objects.filter(detection=detection)])

        properties = {
            'x': round(detection.x, 2),
            'y': round(detection.y, 2),
            'z': round(detection.z, 2),
            'f_sum': round(detection.f_sum, 2),
            'ell_maj': round(detection.ell_maj, 2),
            'ell_min': round(detection.ell_min, 2),
            'w20': round(detection.w20, 2),
            'w50': round(detection.w50, 2),
        }
        # Form content
        params = {
            'title': detection.name,
            'subheading': description,
            'subsubheading': f'{current_idx + 1}/{len(detections_to_resolve)} detections to resolve.',
            'properties': properties,
            'run_id': run_id,
            'detection_id': detection.id,
            'image': mark_safe(img_src),
            'tags': Tag.objects.all(),
        }
        return render(request, 'admin/form_inspect_detection.html', params)

    # Handle POST
    elif request.method == 'POST':
        body = dict(request.POST)
        run = Run.objects.get(id=int(body['run_id'][0]))
        detection = Detection.objects.get(id=int(body['detection_id'][0]))
        detections_to_resolve = Detection.objects.filter(
            run=run,
            n_pix__gte=300,
            rel__gte=0.7
        ).exclude(
            id__in=[sd.detection_id for sd in SourceDetection.objects.all()]
        )
        current_idx = list(detections_to_resolve).index(detection)
        if 'Accept' in body['action']:
            logging.info(f'Marking detection {detection.name} as a real source.')
            source, _ = Source.objects.get_or_create(name=detection.name)
            sd = SourceDetection.objects.create(
                source=source,
                detection=detection
            )

            # add tags and comments if necessary
            add_tag(request, sd)
            add_comment(request, detection)

            new_idx = current_idx + 1
            if new_idx >= len(detections_to_resolve) - 1:
                new_idx = current_idx - 1
            url = f"{reverse('inspect_detection')}?run_id={run.id}&detection_id={detections_to_resolve[new_idx].id}"
            return HttpResponseRedirect(url)
        if 'First' in body['action']:
            url = f"{reverse('inspect_detection')}?run_id={run.id}&detection_id={detections_to_resolve[0].id}"
            return HttpResponseRedirect(url)
        if 'Last' in body['action']:
            idx = len(detections_to_resolve) - 1
            url = f"{reverse('inspect_detection')}?run_id={run.id}&detection_id={detections_to_resolve[idx].id}"
            return HttpResponseRedirect(url)
        if 'Go to index' in body['action']:
            idx = int(request.POST['index'])
            if idx >= len(detections_to_resolve):
                idx = len(detections_to_resolve)
            url = f"{reverse('inspect_detection')}?run_id={run.id}&detection_id={detections_to_resolve[idx - 1].id}"
            return HttpResponseRedirect(url)
        if 'Next' in body['action']:
            new_idx = current_idx + 1
            if new_idx >= len(detections_to_resolve):
                new_idx = len(detections_to_resolve) - 1
            url = f"{reverse('inspect_detection')}?run_id={run.id}&detection_id={detections_to_resolve[new_idx].id}"
            return HttpResponseRedirect(url)
        if 'Previous' in body['action']:
            new_idx = current_idx - 1
            if new_idx <= 0:
                new_idx = 0
            url = f"{reverse('inspect_detection')}?run_id={run.id}&detection_id={detections_to_resolve[new_idx].id}"
            return HttpResponseRedirect(url)
        if 'Delete' in body['action']:
            logging.info(f'Deleting detection {detection.name}.')
            detection.delete()

            new_idx = current_idx + 1
            if new_idx >= len(detections_to_resolve) - 1:
                new_idx = current_idx - 1
            url = f"{reverse('inspect_detection')}?run_id={run.id}&detection_id={detections_to_resolve[new_idx].id}"
            return HttpResponseRedirect(url)
        messages.warning(request, "Selected action that should not exist.")
        url = f"{reverse('inspect_detection')}?run_id={run.id}&detection_id={detections_to_resolve[current_idx].id}"
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
            detection_id__in=[d.id for d in Detection.objects.filter(run=run)]
        )

        if len(conflicts) == 0:
            messages.info(request, "All external conflicts for this run have been resolved")
            return HttpResponseRedirect('/admin/survey/run')

        external_conflict_id = request.GET.get('external_conflict_id', None)
        if external_conflict_id is None:
            # Should only be the case when entering the manual inspection view
            conflict = conflicts[0]
        else:
            conflict = ExternalConflict.objects.get(id=external_conflict_id)
        current_idx = list(conflicts).index(conflict)
        conflict_sd_ids = conflict.conflict_source_detection_ids
        if len(conflict_sd_ids) == 1:
            # Show image
            product = Product.objects.get(detection=conflict.detection)
            img_src = product_summary_image(product, size=(6, 4))
            sd = SourceDetection.objects.filter(detection=conflict.detection)
            description = ''
            if sd:
                tag_sd = TagSourceDetection.objects.filter(source_detection=sd[0])
                if tag_sd:
                    tags = Tag.objects.filter(id__in=[tsd.tag_id for tsd in tag_sd])
                    description += ', '.join([t.name for t in tags])
            description += ', '.join([c.comment for c in Comment.objects.filter(detection=conflict.detection)])
            if description == '':
                description = "No tags or comments"
            properties = {
                'x': round(conflict.detection.x, 2),
                'y': round(conflict.detection.y, 2),
                'z': round(conflict.detection.z, 2),
                'f_sum': round(conflict.detection.f_sum, 2),
                'ell_maj': round(conflict.detection.ell_maj, 2),
                'ell_min': round(conflict.detection.ell_min, 2),
                'w20': round(conflict.detection.w20, 2),
                'w50': round(conflict.detection.w50, 2)
            }

            # Show conflict
            c_sd = SourceDetection.objects.get(id=conflict_sd_ids[0])
            c_detection = c_sd.detection
            # Not all detections have products
            c_product = Product.objects.filter(detection=c_detection)
            if c_product:
                c_product = c_product[0]
            else:
                c_product = None

            c_img_src = product_summary_image(c_product, size=(6, 4))
            c_description = ''
            if c_sd:
                tag_sd = TagSourceDetection.objects.filter(source_detection=c_sd)
                if tag_sd:
                    tags = Tag.objects.filter(id__in=[tsd.tag_id for tsd in tag_sd])
                    c_description += ', '.join([t.name for t in tags])
            c_description += ', '.join([c.comment for c in Comment.objects.filter(detection=c_detection)])
            c_properties = {
                'x': round(c_detection.x, 2),
                'y': round(c_detection.y, 2),
                'z': round(c_detection.z, 2),
                'f_sum': round(c_detection.f_sum, 2),
                'ell_maj': round(c_detection.ell_maj, 2),
                'ell_min': round(c_detection.ell_min, 2),
                'w20': round(c_detection.w20, 2),
                'w50': round(c_detection.w50, 2)
            }
            # Check same survey component for additional functionality
            detection_survey_component = get_survey_component(conflict.detection)
            conflict_survey_component = get_survey_component(c_detection)
            same_survey_component = detection_survey_component == conflict_survey_component

            # Form content
            params = {
                'title': conflict.detection.name,
                'subheading': f'{current_idx + 1}/{len(conflicts)} conflicts to resolve.',
                'name': conflict.detection.name,
                'description': description,
                'image': mark_safe(img_src),
                'properties': properties,
                'conflict_name': c_sd.source.name,
                'conflict_description': c_description,
                'conflict_image': mark_safe(c_img_src),
                'conflict_properties': c_properties,
                'run_id': run_id,
                'external_conflict_id': conflict.id,
                'tags': Tag.objects.all(),
                'same_survey_component': same_survey_component,
            }
            logging.info(f'External conflict {conflict.detection} [{detection_survey_component}] with {c_detection} [{conflict_survey_component}]')
            return render(request, 'admin/form_external_conflict.html', params)
        elif len(conflict_sd_ids) > 1:
            messages.warning(request, "No view has been developed to handle more than one conflict yet...")
            return HttpResponseRedirect('/admin/survey/run')

    # Handle POST
    elif request.method == 'POST':
        body = dict(request.POST)
        run = Run.objects.get(id=int(body['run_id'][0]))
        logging.info(f'External conflict resolution for run {run.name}')
        conflict = ExternalConflict.objects.get(id=int(body['external_conflict_id'][0]))
        conflicts = ExternalConflict.objects.filter(
            detection_id__in=[d.id for d in Detection.objects.filter(run=run)]
        )
        current_idx = list(conflicts).index(conflict)
        if 'Add tags and comments' in body['action']:
            with transaction.atomic():
                sd = SourceDetection.objects.get(detection=conflict.detection)
                sd_conflict = SourceDetection.objects.get(id=conflict.conflict_source_detection_ids[0])
                original_detection = sd_conflict.detection

                # Tag conflict source/detection for current run
                add_tag(request, sd)
                add_comment(request, conflict.detection)

                # Tag conflict source/detection
                add_tag(
                    request,
                    sd_conflict,
                    tag_select_input='tag_select_conflict',
                    tag_create_input='tag_create_conflict'
                )
                add_comment(
                    request,
                    original_detection,
                    comment_input='comment_conflict'
                )
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflict.id}"
            return HttpResponseRedirect(url)
        if 'Go to index' in body['action']:
            idx = int(request.POST['index'])
            if idx >= len(conflicts):
                idx = len(conflicts)
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[idx-1].id}"
            return HttpResponseRedirect(url)
        if 'First' in body['action']:
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[0].id}"
            return HttpResponseRedirect(url)
        if 'Last' in body['action']:
            idx = len(conflicts) - 1
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[idx].id}"
            return HttpResponseRedirect(url)
        if 'Next' in body['action']:
            new_idx = current_idx + 1
            if new_idx >= len(conflicts):
                new_idx = len(conflicts) - 1
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[new_idx].id}"
            return HttpResponseRedirect(url)
        if 'Previous' in body['action']:
            new_idx = current_idx - 1
            if new_idx <= 0:
                new_idx = 0
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[new_idx].id}"
            return HttpResponseRedirect(url)
        if 'Keep new source name' in body['action']:
            with transaction.atomic():
                # Check against existing sources
                new_name = get_release_name(conflict.detection.name)
                if new_name in [s.name for s in Source.objects.all()]:
                    messages.error(request, f"Existing source with name {new_name} exists so cannot accept this detection.")
                    url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[current_idx].id}"
                    return HttpResponseRedirect(url)

                # Accept new name as an official (and separate) source
                logging.info(f'Adding official name {new_name} to detection {conflict.detection.name}')
                sd = SourceDetection.objects.get(detection=conflict.detection)
                source = sd.source
                source.name = new_name
                source.save()
                logging.info("Conflict resolved")
                conflict.delete()

            new_idx = current_idx + 1
            if new_idx >= len(conflicts):
                new_idx = current_idx - 1
            if len(conflicts) == 1:
                return HttpResponseRedirect('/admin/survey/run')
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[new_idx].id}"
            return HttpResponseRedirect(url)
        if 'Ignore conflict' in body['action']:
            logging.info(f'Ignoring conflict {conflict.id}. Deleting conflict instance.')
            conflict.delete()
            new_idx = current_idx + 1
            if new_idx >= len(conflicts):
                new_idx = current_idx - 1
            if len(conflicts) == 1:
                return HttpResponseRedirect('/admin/survey/run')
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[new_idx].id}"
            return HttpResponseRedirect(url)
        if 'Delete conflict' in body['action']:
            deleted_other_conflict = False
            with transaction.atomic():
                # Remove any conflicts that may have previously been accepted
                sds = SourceDetection.objects.filter(
                    detection=conflict.detection
                )
                for sd in sds:
                    source = sd.source
                    ssd = SourceDetection.objects.filter(source=source)
                    # Delete source if this is the only detection (create new)
                    if (len(ssd) == 1) and (ssd[0] == sd):
                        logging.info(f'Deleting source {source.name}.')
                        sd.delete()
                        source.delete()
                        deleted_other_conflict = True
                    # Delete only the source detection if a source existed already (rename)
                    else:
                        logging.info(f'Deleting source detection (id={sd.id}) since related source has been released.')
                        sd.delete()
                        deleted_other_conflict = True
                logging.info("Conflict resolved")
                conflict.delete()

                # Remove other possible conflicts with this detection.
                other_conflicts = ExternalConflict.objects.filter(detection=conflict.detection)
                logging.info(f'Other conflicts id={[c.id for c in other_conflicts]} can also be resolved')
                for c in other_conflicts:
                    c.delete()

            new_idx = current_idx + 1
            if new_idx >= len(conflicts):
                new_idx = current_idx - 1
            if len(conflicts) == 1:
                return HttpResponseRedirect('/admin/survey/run')
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[new_idx].id}"
            if deleted_other_conflict:
                conflicts = ExternalConflict.objects.filter(
                    detection_id__in=[d.id for d in Detection.objects.filter(run=run)]
                )
                url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[current_idx].id}"
            return HttpResponseRedirect(url)
        if 'Copy old source name' in body['action']:
            with transaction.atomic():
                # Priority over creating new name. Undo create new name if exists
                sds = SourceDetection.objects.filter(
                    detection=conflict.detection)

                # Remove new name source if exists.
                for sd in sds:
                    source = sd.source
                    ssd = SourceDetection.objects.filter(source=source)
                    # Delete source if this is the only detection (create new)
                    if (len(ssd) == 1) and (ssd[0] == sd) and (settings.PROJECT in source.name):
                        logging.info(f'Deleting source {source.name}.')
                        sd.delete()
                        source.delete()

                detection = conflict.detection
                sd_ids = conflict.conflict_source_detection_ids
                if len(sd_ids) != 1:
                    messages.error(request, f"Cannot add new detection {detection.name} to existing source if there are multiple potential sources.")
                sd_id = sd_ids[0]

                # Delete existing source and update source detection
                sd_existing = SourceDetection.objects.get(detection=detection)
                new_source = SourceDetection.objects.get(id=sd_id).source
                old_source = sd_existing.source
                sd_existing.source = new_source
                logging.info(f'Adding detection {detection.name} to existing source {new_source.name}.')
                sd_existing.save()
                logging.info("Conflict resolved")
                conflict.delete()

            new_idx = current_idx + 1
            if new_idx >= len(conflicts):
                # TODO: crashes if this is not correct.
                new_idx = current_idx - 1
            if len(conflicts) == 1:
                return HttpResponseRedirect('/admin/survey/run')
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[new_idx].id}"
            return HttpResponseRedirect(url)
        if 'Replace detection in source' in body['action']:
            detection = conflict.detection
            sd = SourceDetection.objects.get(id=conflict.conflict_source_detection_ids[0])
            source = sd.source
            logging.info(f'Replacing detection {sd.detection} with {detection} in source {source}.')

            with transaction.atomic():
                logging.info('Database update')
                current_sd = SourceDetection.objects.get(detection=detection)
                current_sd.source = source
                current_sd.save()
                sd.delete()

            new_idx = current_idx + 1
            if new_idx >= len(conflicts):
                new_idx = current_idx - 1
            if len(conflicts) == 1:
                return HttpResponseRedirect('/admin/survey/run')
            url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[new_idx].id}"
            return HttpResponseRedirect(url)
        messages.warning(request, "Selected action that should not exist.")
        url = f"{reverse('external_conflict')}?run_id={run.id}&external_conflict_id={conflicts[current_idx].id}"
        return HttpResponseRedirect(url)
    else:
        messages.warning(request, "Error, returning to run.")
        return HttpResponseRedirect('/admin/survey/run')
