"""The admin columns and the manual inspection properties of the gaskap module."""

import pytest
from django.conf import settings

from modules.core.models import Detection

if "gaskap" not in settings.MODULES:
    pytest.skip("gaskap module is not installed", allow_module_level=True)

COLUMNS = ["Glong[deg]", "Glat[deg]", "Peak_flux[Jy]", "Vel_peak[km/s]", "Vel_range[km/s]", "RMS[mJy]", "SNR"]


@pytest.fixture
def peaks(survey):
    Detection.objects.filter(run=survey.run).update(
        l=335.5, b=-1.25, l_peak=335.1234, b_peak=-1.5678, freq_peak=1.42e9, x_peak=3, y_peak=4, z_peak=5
    )
    survey.instance.parameters = {"input.data": "/cubes/test.fits"}
    survey.instance.save(update_fields=["parameters"])
    return survey


@pytest.mark.parametrize("page", ["accepteddetection", "rejecteddetection"])
@pytest.mark.parametrize("query", ["", "?run={run}"])
def test_peak_columns(admin_client, peaks, page, query):
    content = admin_client.get(f"/admin/survey/{page}/{query.format(run=peaks.run.id)}").content.decode()
    for column in COLUMNS:
        assert column in content
    assert "335.1234" in content
    # 0.01 Jy
    assert ">10.0<" in content
    assert "ell maj" not in content
    assert "moment0" not in content


def test_carta_column(admin_client, peaks, settings):
    settings.CARTA_URL = "https://carta.example.org"
    content = admin_client.get(f"/admin/survey/accepteddetection/?run={peaks.run.id}").content.decode()
    assert "https://carta.example.org?file=/cubes/test.fits" in content
    content = admin_client.get(f"/admin/survey/rejecteddetection/?run={peaks.run.id}").content.decode()
    assert "carta.example.org" not in content


def test_detail_pages(admin_client, peaks):
    assert admin_client.get(f"/admin/survey/accepteddetection/{peaks.accepted.id}/change/").status_code == 200
    assert admin_client.get(f"/admin/survey/rejecteddetection/{peaks.rejected.id}/change/").status_code == 200


def test_detection_list_in_galactic_coordinates(admin_client, peaks):
    content = admin_client.get(f"/admin/survey/detection/?run={peaks.run.id}").content.decode()
    assert "Glong[deg]" in content and "335.5" in content
    assert ">RA<" not in content


def test_run_page_columns(admin_client, peaks):
    content = admin_client.get("/admin/survey/run/").content.decode()
    assert "Accepted Detections" in content and "Rejected Detections" in content
    assert "Manual inspection" in content
    assert "Unresolved Detections" not in content
    assert "column-sanity_thresholds" not in content


def test_inspection_page(admin_client, peaks):
    content = admin_client.get(f"/inspect_detection?run_id={peaks.run.id}").content.decode()
    for column in COLUMNS:
        assert column in content
    assert "f_sum" not in content
    assert 'value="RFI"' not in content
    assert 'value="Reject"' in content


def test_empty_values(admin_client, survey):
    """Detections without the peak properties."""
    assert admin_client.get(f"/admin/survey/accepteddetection/?run={survey.run.id}").status_code == 200
    assert admin_client.get(f"/inspect_detection?run_id={survey.run.id}").status_code == 200
