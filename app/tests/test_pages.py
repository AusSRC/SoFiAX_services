"""Navigation to the basic pages."""

import pytest

# Formatted with the ids of the objects created by the survey fixture
PAGES = [
    "/admin/",
    "/admin/survey/run/",
    "/admin/survey/run/{run}/change/",
    "/admin/survey/instance/",
    "/admin/survey/detection/?run={run}",
    "/admin/survey/accepteddetection/",
    "/admin/survey/accepteddetection/?run={run}",
    "/admin/survey/accepteddetection/{accepted}/change/",
    "/admin/survey/rejecteddetection/",
    "/admin/survey/rejecteddetection/?run={run}",
    "/admin/survey/rejecteddetection/{rejected}/change/",
    "/admin/survey/unresolveddetection/",
    "/admin/survey/tag/",
    "/admin/survey/comment/",
    "/admin/survey/task/",
    "/inspect_detection?run_id={run}",
    "/summary_image?id={pending}",
]


@pytest.mark.parametrize("page", PAGES)
def test_page_loads(admin_client, survey, page):
    url = page.format(
        run=survey.run.id,
        pending=survey.pending.id,
        accepted=survey.accepted.id,
        rejected=survey.rejected.id,
    )
    response = admin_client.get(url)
    assert response.status_code == 200


def test_admin_requires_login(client, db):
    response = client.get("/admin/")
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


def test_accepted_list_shows_only_accepted(admin_client, survey):
    content = admin_client.get(f"/admin/survey/accepteddetection/?run={survey.run.id}").content.decode()
    assert survey.accepted.name in content
    assert survey.rejected.name not in content
    assert survey.pending.name not in content


def test_rejected_list_shows_only_rejected(admin_client, survey):
    content = admin_client.get(f"/admin/survey/rejecteddetection/?run={survey.run.id}").content.decode()
    assert survey.rejected.name in content
    assert survey.accepted.name not in content
    assert survey.pending.name not in content
