"""The pages change with the modules that are installed."""

import pytest
from django.conf import settings

from modules.core.models import Detection


def installed(module):
    return pytest.mark.skipif(module not in settings.MODULES, reason=f"{module} module is not installed")


def not_installed(module):
    return pytest.mark.skipif(module in settings.MODULES, reason=f"{module} module is installed")


@not_installed("operations")
def test_core_run_page_has_no_operations(admin_client, survey):
    content = admin_client.get("/admin/survey/run/").content.decode()
    assert "External conflicts" not in content
    assert "_external_cross_match" not in content
    assert 'value="_download_summaries"' in content
    assert admin_client.get("/external_conflict?run_id=1").status_code == 404


@installed("operations")
def test_operations_pages(admin_client, survey):
    assert admin_client.get("/admin/operations/observation/").status_code == 200
    assert admin_client.get("/admin/operations/surveycomponent/").status_code == 200
    assert admin_client.get("/api/observations/").status_code == 200


@installed("wallaby")
def test_wallaby_pages(admin_client, survey):
    for page in ["tile", "sourceextractionregion", "kinematicmodel", "kinematicmodel_3kidnas"]:
        assert admin_client.get(f"/admin/wallaby/{page}/").status_code == 200, page
    assert admin_client.get("/api/tiles/").status_code == 200
    assert admin_client.get("/api/sers/").status_code == 200


@installed("wallaby")
def test_released_detection_is_marked_for_kinematic_modelling(survey):
    from modules.operations.signals import detection_released
    from modules.wallaby.models import KinematicModelState

    detection_released.send(sender=Detection, detection=survey.accepted)
    assert KinematicModelState.objects.filter(detection=survey.accepted, attempted=0).exists()


@installed("dingo")
def test_gama_matches(admin_client, survey):
    from modules.dingo.models import DetectionNearestGAMA

    DetectionNearestGAMA.objects.create(detection_id=survey.accepted, cata_id=424242)
    DetectionNearestGAMA.objects.create(detection_id=survey.pending, cata_id=535353)

    content = admin_client.get(f"/admin/survey/accepteddetection/?run={survey.run.id}").content.decode()
    assert "424242" in content
    content = admin_client.get(f"/inspect_detection?run_id={survey.run.id}").content.decode()
    assert "GAMA" in content and "535353" in content


@not_installed("dingo")
def test_no_gama_matches(admin_client, survey):
    content = admin_client.get(f"/admin/survey/accepteddetection/?run={survey.run.id}").content.decode()
    assert "GAMA" not in content
