"""Catalogue of the detections of a run (core module)."""

from django.http import HttpResponse
from modules.core.models import Detection, Instance
from modules.core.views.common import _attachment, _id_parameter


def _build_detection(detection):
    det = (
        f"<TR>\n"
        f"<TD>{detection.name}</TD>\n"
        f"<TD>{detection.id}</TD>\n"
        f"<TD>{detection.x}</TD>\n"
        f"<TD>{detection.y}</TD>\n"
        f"<TD>{detection.z}</TD>\n"
        f"<TD>{detection.x_min}</TD>\n"
        f"<TD>{detection.x_max}</TD>\n"
        f"<TD>{detection.y_min}</TD>\n"
        f"<TD>{detection.y_max}</TD>\n"
        f"<TD>{detection.z_min}</TD>\n"
        f"<TD>{detection.z_max}</TD>\n"
        f"<TD>{detection.n_pix}</TD>\n"
        f"<TD>{detection.f_min}</TD>\n"
        f"<TD>{detection.f_max}</TD>\n"
        f"<TD>{detection.f_sum}</TD>\n"
        f"<TD>{'' if detection.rel is None else detection.rel}</TD>\n"
        f"<TD>{detection.flag}</TD>\n"
        f"<TD>{detection.rms}</TD>\n"
        f"<TD>{detection.w20}</TD>\n"
        f"<TD>{detection.w50}</TD>\n"
        f"<TD>{detection.ell_maj}</TD>\n"
        f"<TD>{detection.ell_min}</TD>\n"
        f"<TD>{detection.ell_pa}</TD>\n"
        f"<TD>{detection.ell3s_maj}</TD>\n"
        f"<TD>{detection.ell3s_min}</TD>\n"
        f"<TD>{detection.ell3s_pa}</TD>\n"
        f"<TD>{'' if detection.kin_pa is None else detection.kin_pa}</TD>\n"
        f"<TD>{detection.err_x}</TD>\n"
        f"<TD>{detection.err_y}</TD>\n"
        f"<TD>{detection.err_z}</TD>\n"
        f"<TD>{detection.err_f_sum}</TD>\n"
        f"<TD>{'' if detection.ra is None else detection.ra}</TD>\n"
        f"<TD>{'' if detection.dec is None else detection.dec}</TD>\n"
        f"<TD>{'' if detection.freq is None else detection.freq}</TD>\n"
        f"<TD>{'' if detection.l is None else detection.l}</TD>\n"
        f"<TD>{'' if detection.b is None else detection.b}</TD>\n"
        f"<TD>{'' if detection.v_rad is None else detection.v_rad}</TD>\n"
        f"<TD>{'' if detection.v_opt is None else detection.v_opt}</TD>\n"
        f"<TD>{'' if detection.v_app is None else detection.v_app}</TD>\n"
        f"</TR>\n"
    )
    return det


def _build_catalog(detections, date, version):
    cat = (
        f'<?xml version="1.0" ?>\n'
        f'<VOTABLE version="1.3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        f'xmlns="http://www.ivoa.net/xml/VOTable/v1.3">\n'
        f"<RESOURCE>\n"
        f"<DESCRIPTION>Source catalogue created by the Source Finding Application(SoFiA)</DESCRIPTION>\n"
        f'<PARAM name="Creator" datatype="char" arraysize="*" value="{"" if version is None else version}"'
        f' ucd="meta.id;meta.software"/>\n'
        f'<PARAM name="Time" datatype="char" arraysize="*" value="{date}" '
        f'ucd="time.creation"/>\n'
        f'<TABLE ID="SoFiA_source_catalogue" name="SoFiA source catalogue">\n'
        f'<FIELD arraysize="32" datatype="char" name="name" unit="" ucd="meta.id"/>\n'
        f'<FIELD datatype="long" name="id" unit="" ucd="meta.id"/>\n'
        f'<FIELD datatype="double" name="x" unit="pix" ucd="pos.cartesian.x"/>\n'
        f'<FIELD datatype="double" name="y" unit="pix" ucd="pos.cartesian.y"/>\n'
        f'<FIELD datatype="double" name="z" unit="pix" ucd="pos.cartesian.z"/>\n'
        f'<FIELD datatype="long" name="x_min" unit="pix" ucd="pos.cartesian.x;stat.min"/>\n'
        f'<FIELD datatype="long" name="x_max" unit="pix" ucd="pos.cartesian.x;stat.max"/>\n'
        f'<FIELD datatype="long" name="y_min" unit="pix" ucd="pos.cartesian.y;stat.min"/>\n'
        f'<FIELD datatype="long" name="y_max" unit="pix" ucd="pos.cartesian.y;stat.max"/>\n'
        f'<FIELD datatype="long" name="z_min" unit="pix" ucd="pos.cartesian.z;stat.min"/>\n'
        f'<FIELD datatype="long" name="z_max" unit="pix" ucd="pos.cartesian.z;stat.max"/>\n'
        f'<FIELD datatype="long" name="n_pix" unit="" ucd="meta.number;instr.pixel"/>\n'
        f'<FIELD datatype="double" name="f_min" unit="Jy/beam" ucd="phot.flux.density;stat.min"/>\n'
        f'<FIELD datatype="double" name="f_max" unit="Jy/beam" ucd="phot.flux.density;stat.max"/>\n'
        f'<FIELD datatype="double" name="f_sum" unit="Jy*Hz" ucd="phot.flux"/>\n'
        f'<FIELD datatype="double" name="rel" unit="" ucd="stat.probability"/>\n'
        f'<FIELD datatype="long" name="flag" unit="" ucd="meta.code.qual"/>\n'
        f'<FIELD datatype="double" name="rms" unit="Jy/beam" ucd="instr.det.noise"/>\n'
        f'<FIELD datatype="double" name="w20" unit="Hz" ucd="spect.line.width"/>\n'
        f'<FIELD datatype="double" name="w50" unit="Hz" ucd="spect.line.width"/>\n'
        f'<FIELD datatype="double" name="ell_maj" unit="pix" ucd="phys.angSize"/>\n'
        f'<FIELD datatype="double" name="ell_min" unit="pix" ucd="phys.angSize"/>\n'
        f'<FIELD datatype="double" name="ell_pa" unit="deg" ucd="pos.posAng"/>\n'
        f'<FIELD datatype="double" name="ell3s_maj" unit="pix" ucd="phys.angSize"/>\n'
        f'<FIELD datatype="double" name="ell3s_min" unit="pix" ucd="phys.angSize"/>\n'
        f'<FIELD datatype="double" name="ell3s_pa" unit="deg" ucd="pos.posAng"/>\n'
        f'<FIELD datatype="double" name="kin_pa" unit="deg" ucd="pos.posAng"/>\n'
        f'<FIELD datatype="double" name="err_x" unit="pix" ucd="stat.error;pos.cartesian.x"/>\n'
        f'<FIELD datatype="double" name="err_y" unit="pix" ucd="stat.error;pos.cartesian.y"/>\n'
        f'<FIELD datatype="double" name="err_z" unit="pix" ucd="stat.error;pos.cartesian.z"/>\n'
        f'<FIELD datatype="double" name="err_f_sum" unit="Jy*Hz" ucd="stat.error;phot.flux"/>\n'
        f'<FIELD datatype="double" name="ra" unit="deg" ucd="pos.eq.ra"/>\n'
        f'<FIELD datatype="double" name="dec" unit="deg" ucd="pos.eq.dec"/>\n'
        f'<FIELD datatype="double" name="freq" unit="Hz" ucd="em.freq"/>\n'
        f'<FIELD datatype="double" name="l" unit="deg" ucd="pos.galactic.lon"/>\n'
        f'<FIELD datatype="double" name="b" unit="deg" ucd="pos.galactic.lat"/>\n'
        f'<FIELD datatype="double" name="v_rad" unit="m/s" ucd="spect.dopplerVeloc.radio"/>\n'
        f'<FIELD datatype="double" name="v_opt" unit="m/s" ucd="spect.dopplerVeloc.opt"/>\n'
        f'<FIELD datatype="double" name="v_app" unit="m/s" ucd="spect.dopplerVeloc"/>\n'
        f"<DATA>\n"
        f"<TABLEDATA>\n"
        f"{''.join([_build_detection(detection) for detection in detections])}"
        f"</TABLEDATA>\n"
        f"</DATA>\n"
        f"</TABLE>\n"
        f"</RESOURCE>\n"
        f"</VOTABLE>\n"
    )
    return cat


def run_catalog(request):
    run_id, error = _id_parameter(request)
    if error:
        return error

    detections = Detection.objects.filter(run=run_id)
    if not detections:
        return HttpResponse("no detections found.", status=404)

    instance = Instance.objects.filter(run=run_id).order_by("-run_date").first()
    if not instance:
        return HttpResponse("no instance found.", status=404)

    cat = _build_catalog(detections, instance.run_date, instance.version)
    return _attachment(cat, f"{run_id}_{detections[0].run.name}.xml", "text/xml")
