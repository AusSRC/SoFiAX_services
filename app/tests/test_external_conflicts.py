"""Resolving external conflicts, and the additions of the operations module to the run page."""

import pytest
from django.conf import settings
from django.utils import timezone

if "operations" not in settings.MODULES:
    pytest.skip("operations module is not installed", allow_module_level=True)

from modules.core.models import Run  # noqa: E402
from modules.operations.models import ExternalConflict, SurveyComponent, SurveyComponentRun  # noqa: E402

from .conftest import create_detection  # noqa: E402

URL = "/external_conflict"


@pytest.fixture
def conflicts(survey):
    """Two accepted detections of the run in conflict with a released source of another run."""
    other_run = Run.objects.create(name="other_run", sanity_thresholds={}, created=timezone.now())
    component = SurveyComponent.objects.create(name="component", runs=[])
    for run in (survey.run, other_run):
        SurveyComponentRun.objects.create(run=run, sc=component)

    source = create_detection(other_run, survey.instance, "source_1", True, 10)
    source.source_name = "TEST J000000-000000"
    source.save(update_fields=["source_name"])

    second = create_detection(survey.run, survey.instance, "accepted_2", True, 11)
    return [
        ExternalConflict.objects.create(run=survey.run, detection=detection, conflict_detection=source)
        for detection in (survey.accepted, second)
    ]


def test_conflict_page_loads(admin_client, survey, conflicts):
    response = admin_client.get(f"{URL}?run_id={survey.run.id}")
    assert response.status_code == 200
    assert "1/2 conflicts to resolve" in response.content.decode()


def test_next_conflict(admin_client, survey, conflicts):
    response = admin_client.post(
        URL, {"run_id": survey.run.id, "external_conflict_id": conflicts[0].id, "action": "Next", "index": ""}
    )
    assert response.status_code == 302
    assert response["Location"] == f"{URL}?run_id={survey.run.id}&external_conflict_id={conflicts[1].id}"


def test_copy_old_source_name(admin_client, survey, conflicts):
    response = admin_client.post(
        URL, {"run_id": survey.run.id, "external_conflict_id": conflicts[0].id, "action": "Copy old source name"}
    )
    assert response.status_code == 302
    survey.accepted.refresh_from_db()
    assert survey.accepted.source_name == "TEST J000000-000000"
    assert not ExternalConflict.objects.filter(id=conflicts[0].id).exists()
    assert ExternalConflict.objects.filter(id=conflicts[1].id).exists()


def test_delete_conflict(admin_client, survey, conflicts):
    response = admin_client.post(
        URL, {"run_id": survey.run.id, "external_conflict_id": conflicts[0].id, "action": "Delete conflict"}
    )
    assert response.status_code == 302
    survey.accepted.refresh_from_db()
    assert survey.accepted.accepted is None
    assert not ExternalConflict.objects.filter(detection=survey.accepted).exists()


def test_no_conflicts_redirects_to_runs(admin_client, survey):
    SurveyComponentRun.objects.create(run=survey.run, sc=SurveyComponent.objects.create(name="component", runs=[]))
    response = admin_client.get(f"{URL}?run_id={survey.run.id}")
    assert response.status_code == 302
    assert response["Location"] == "/admin/survey/run"


def test_run_page_has_operations(admin_client, survey):
    content = admin_client.get("/admin/survey/run/").content.decode()
    assert "External conflicts" in content
    for action in ["_internal_cross_match", "_external_cross_match", "_release_sources", "_auto_assign_to_component"]:
        assert f'value="{action}"' in content
