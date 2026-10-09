"""Accepting and rejecting detections, and adding comments and tags."""

from survey.models import Comment, Tag, TagDetection

INSPECT_URL = "/inspect_detection"


def inspect(client, survey, detection, action, comment="", tag_create="", tag_select="None"):
    """Submit the manual inspection form for a detection."""
    return client.post(
        INSPECT_URL,
        {
            "run_id": survey.run.id,
            "detection_id": detection.id,
            "action": action,
            "comment": comment,
            "tag_create": tag_create,
            "tag_select": tag_select,
        },
    )


def tags_of(detection):
    return [td.tag.name for td in TagDetection.objects.filter(detection=detection)]


def test_queue_has_only_uninspected_detections(admin_client, survey):
    content = admin_client.get(f"{INSPECT_URL}?run_id={survey.run.id}").content.decode()
    assert "1/2 detections to resolve" in content


def test_accept(admin_client, survey):
    response = inspect(admin_client, survey, survey.pending, "Accept")
    assert response.status_code == 302
    survey.pending.refresh_from_db()
    assert survey.pending.accepted is True


def test_reject(admin_client, survey):
    response = inspect(admin_client, survey, survey.pending, "Reject")
    assert response.status_code == 302
    survey.pending.refresh_from_db()
    assert survey.pending.accepted is False
    assert tags_of(survey.pending) == []


def test_rfi_rejects_and_adds_tag(admin_client, survey):
    response = inspect(admin_client, survey, survey.pending, "RFI")
    assert response.status_code == 302
    survey.pending.refresh_from_db()
    assert survey.pending.accepted is False
    assert tags_of(survey.pending) == ["RFI"]


def test_inspected_detection_leaves_queue(admin_client, survey):
    inspect(admin_client, survey, survey.pending, "Accept")
    content = admin_client.get(f"{INSPECT_URL}?run_id={survey.run.id}").content.decode()
    assert "1/1 detections to resolve" in content


def test_empty_queue_redirects_to_runs(admin_client, survey):
    inspect(admin_client, survey, survey.pending, "Accept")
    inspect(admin_client, survey, survey.pending_2, "Reject")
    response = admin_client.get(f"{INSPECT_URL}?run_id={survey.run.id}")
    assert response.status_code == 302
    assert response["Location"] == "/admin/survey/run"


def test_add_comment(admin_client, survey):
    inspect(admin_client, survey, survey.pending, "Accept", comment="looks real")
    comment = Comment.objects.get(detection=survey.pending)
    assert comment.comment == "looks real"
    assert comment.author == "admin"


def test_no_comment_when_left_empty(admin_client, survey):
    inspect(admin_client, survey, survey.pending, "Accept")
    assert not Comment.objects.filter(detection=survey.pending).exists()


def test_create_tag(admin_client, survey):
    inspect(admin_client, survey, survey.pending, "Accept", tag_create="interesting")
    assert Tag.objects.filter(name="interesting").exists()
    assert tags_of(survey.pending) == ["interesting"]


def test_select_existing_tag(admin_client, survey):
    tag = Tag.objects.create(name="follow up")
    inspect(admin_client, survey, survey.pending, "Reject", tag_select=str(tag.id))
    assert tags_of(survey.pending) == ["follow up"]


def test_deselect_returns_accepted_detection_to_queue(admin_client, survey):
    response = admin_client.post(
        f"/admin/survey/accepteddetection/?run={survey.run.id}",
        {"action": "deselect", "_selected_action": [survey.accepted.id]},
    )
    assert response.status_code == 302
    survey.accepted.refresh_from_db()
    assert survey.accepted.accepted is None


def test_reopen_returns_rejected_detection_to_queue(admin_client, survey):
    response = admin_client.post(
        f"/admin/survey/rejecteddetection/?run={survey.run.id}",
        {"action": "reopen", "_selected_action": [survey.rejected.id]},
    )
    assert response.status_code == 302
    survey.rejected.refresh_from_db()
    assert survey.rejected.accepted is None
