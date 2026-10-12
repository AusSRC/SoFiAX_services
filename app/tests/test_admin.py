"""Admin lists and the actions on detections."""

import pytest
from django.contrib import admin
from django.urls import reverse

from modules.core.models import Comment, TagDetection


def registered_lists():
    return [
        reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist") for model in admin.site._registry
    ]


def test_registered_admin_lists_load(admin_client, survey):
    """Every list in the admin, whatever the project and modules that are configured."""
    for url in registered_lists():
        response = admin_client.get(url)
        assert response.status_code == 200, url


@pytest.mark.parametrize("action", ["add_tag", "add_comment"])
def test_action_shows_form(admin_client, survey, action):
    response = admin_client.post(
        f"/admin/survey/detection/?run={survey.run.id}",
        {"action": action, "_selected_action": [survey.pending.id]},
    )
    assert response.status_code == 200
    assert not TagDetection.objects.filter(detection=survey.pending).exists()
    assert not Comment.objects.filter(detection=survey.pending).exists()


def test_add_tag_action(admin_client, survey):
    selected = [survey.pending.id, survey.pending_2.id]
    response = admin_client.post(
        f"/admin/survey/detection/?run={survey.run.id}",
        {
            "action": "add_tag",
            "_selected_action": selected,
            "confirm": "yes",
            "tag_create": "bulk",
            "tag_select": "None",
        },
    )
    assert response.status_code == 302
    tagged = TagDetection.objects.filter(tag__name="bulk").values_list("detection_id", flat=True)
    assert sorted(tagged) == sorted(selected)


def test_add_comment_action(admin_client, survey):
    response = admin_client.post(
        f"/admin/survey/detection/?run={survey.run.id}",
        {"action": "add_comment", "_selected_action": [survey.pending.id], "confirm": "yes", "comment": "check this"},
    )
    assert response.status_code == 302
    assert Comment.objects.get(detection=survey.pending).comment == "check this"
