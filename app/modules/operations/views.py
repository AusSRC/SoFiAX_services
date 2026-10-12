"""Resolving external conflicts."""

import logging
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from modules.core.models import Detection, Product, Run, Tag, TagDetection
from modules.core.utils.forms import _add_comment, _add_tag
from modules.core.utils.plot import product_summary_image
from modules.core.utils.views import handle_navigation, handle_next
from modules.operations.components import get_release_name, get_survey_component
from modules.operations.models import ExternalConflict


logging.basicConfig(level=logging.INFO)


# TODO: require superuser status
def _run_conflicts(run):
    """External conflicts of the detections of a run."""
    return ExternalConflict.objects.filter(detection_id__in=[d.id for d in Detection.objects.filter(run=run)])


def _remove_conflicts(conflicts, detection, run):
    """Remove the external conflicts of a detection and return the remaining conflicts of the run."""
    for c in conflicts:
        if c.detection == detection:
            logging.info(f"Removing external conflict for this detection: {c.id}")
            c.delete()
    return _run_conflicts(run)


def _conflict_properties(detection):
    return {
        field: round(getattr(detection, field), 2)
        for field in ["x", "y", "z", "f_sum", "ell_maj", "ell_min", "w20", "w50"]
    }


def external_conflict_view(request):
    if request.method == "GET":
        run_id = request.GET.get("run_id", None)
        if not run_id:
            raise Exception("Run not selected or does not exist.")
        try:
            run_id = int(run_id)
        except ValueError:
            return HttpResponse("Run id is not an integer.", status=400)

        run = Run.objects.get(id=run_id)
        conflicts = _run_conflicts(run)
        if len(conflicts) == 0:
            messages.info(request, "All external conflicts for this run have been resolved")
            return HttpResponseRedirect("/admin/survey/run")

        ex_c_id = int(request.GET.get("external_conflict_id", conflicts[0].id))
        ex_c = ExternalConflict.objects.get(id=ex_c_id)
        idx = list(conflicts).index(ex_c)

        # Show image
        product = Product.objects.get(detection=ex_c.detection)
        img_src = product_summary_image(product, size=(6, 4))
        properties = _conflict_properties(ex_c.detection)

        # Show conflict
        c_product = Product.objects.get(detection=ex_c.conflict_detection)
        c_img_src = product_summary_image(c_product, size=(6, 4))
        c_properties = _conflict_properties(ex_c.conflict_detection)
        # Check same survey component for additional functionality
        detection_survey_component = get_survey_component(ex_c.detection)
        conflict_survey_component = get_survey_component(ex_c.conflict_detection)
        same_survey_component = detection_survey_component == conflict_survey_component

        # Form content
        params = {
            "title": ex_c.detection.name,
            "subheading": f"{idx + 1}/{len(conflicts)} conflicts to resolve.",
            "name": ex_c.detection.name,
            "description": ex_c.detection.description_string(),
            "image": mark_safe(img_src),
            "properties": properties,
            "conflict_name": ex_c.conflict_detection.source_name,
            "conflict_description": ex_c.conflict_detection.description_string(),
            "conflict_image": mark_safe(c_img_src),
            "conflict_properties": c_properties,
            "run_id": run_id,
            "external_conflict_id": ex_c.id,
            "tags": Tag.objects.all(),
            "same_survey_component": same_survey_component,
        }
        logging.info(
            f"External conflict {ex_c.detection} [{detection_survey_component}] with {ex_c.conflict_detection} [{conflict_survey_component}]"
        )
        return render(request, "admin/form_external_conflict.html", params)

    # Handle POST
    elif request.method == "POST":
        body = dict(request.POST)
        run = Run.objects.get(id=int(body["run_id"][0]))
        logging.info(f"External conflict resolution for run {run.name}")
        ex_c = ExternalConflict.objects.get(id=int(body["external_conflict_id"][0]))
        conflicts = _run_conflicts(run)
        idx = list(conflicts).index(ex_c)
        url_base = reverse("external_conflict")
        url_params = f"run_id={run.id}&external_conflict_id="

        if "Add tags and comments" in body["action"]:
            with transaction.atomic():
                # Tag both detections in conflict
                _add_tag(request, ex_c.detection)
                _add_comment(request, ex_c.detection)
                _add_tag(
                    request,
                    ex_c.conflict_detection,
                    tag_select_input="tag_select_conflict",
                    tag_create_input="tag_create_conflict",
                )
                _add_comment(request, ex_c.conflict_detection, comment_input="comment_conflict")
            url = f"{url_base}?{url_params}{ex_c.id}"
            return HttpResponseRedirect(url)

        if "Keep new source name" in body["action"]:
            with transaction.atomic():
                # Check against existing sources
                new_name = get_release_name(ex_c.detection.name)
                if new_name in [
                    d.source_name
                    for d in Detection.objects.filter(accepted=True, source_name__isnull=False).exclude(
                        id=ex_c.detection.id
                    )
                ]:
                    messages.error(
                        request,
                        f"Existing source with name {new_name} exists so cannot accept this detection.",
                    )
                    url = f"{url_base}?{url_params}{conflicts[idx].id}"
                    return HttpResponseRedirect(url)
                # Accept new name as an official (and separate) source
                logging.info(f"Adding official name {new_name} to detection {ex_c.detection.name}")
                ex_c.detection.source_name = new_name
                ex_c.detection.save()
                conflicts = _remove_conflicts(conflicts, ex_c.detection, run)
            url = handle_next(request, conflicts, idx, url_base, url_params)
            return HttpResponseRedirect(url)

        if "Copy old source name" in body["action"]:
            with transaction.atomic():
                logging.info(
                    f"Adding existing source name {ex_c.conflict_detection.source_name} to current detection {ex_c.detection.name}."
                )
                ex_c.detection.source_name = ex_c.conflict_detection.source_name
                ex_c.detection.save()
                ex_c.delete()
            url = handle_next(request, conflicts, idx, url_base, url_params)
            return HttpResponseRedirect(url)

        if "Replace detection in source" in body["action"]:
            source_name = ex_c.conflict_detection.source_name
            logging.info(
                f"Replacing detection {ex_c.conflict_detection} with {ex_c.detection} in source {source_name}."
            )
            with transaction.atomic():
                ex_c.detection.source_name = source_name
                ex_c.detection.save()
                ex_c.conflict_detection.source_name = None
                ex_c.conflict_detection.save()

                # Remove release tag detection entry for replaced detection
                remove_tagdetections = TagDetection.objects.filter(
                    detection=ex_c.conflict_detection, tag__type="release"
                )
                for td in remove_tagdetections:
                    logging.info(
                        f"Removing tag detection objects: {td.id} [tag: {td.tag_id}, detection: {td.detection_id}]"
                    )
                    td.delete()

                conflicts = _remove_conflicts(conflicts, ex_c.detection, run)
            url = handle_next(request, conflicts, idx, url_base, url_params)
            return HttpResponseRedirect(url)

        if "Delete conflict" in body["action"]:
            with transaction.atomic():
                # Remove any conflicts that may have previously been accepted for this detection
                logging.info(f"De-selecting detection {ex_c.detection}")
                ex_c.detection.source_name = None
                ex_c.detection.accepted = None
                ex_c.detection.save(update_fields=["source_name", "accepted"])

                # Remove external conflicts
                logging.info(f"Deleting external conflicts for detection {ex_c.detection}")
                for c in ExternalConflict.objects.filter(detection=ex_c.detection):
                    c.delete()
                # NOTE: issue with indexing here if multiple conflicts have been deleted
                url = handle_next(request, conflicts, idx, url_base, url_params)
            return HttpResponseRedirect(url)

        url = handle_navigation(request, conflicts, idx, url_base, url_params)
        if not url:
            messages.warning(request, "Selected action that should not exist.")
            url = f"{url_base}?{url_params}{conflicts[idx].id}"
        return HttpResponseRedirect(url)
    else:
        messages.warning(request, "Error, returning to run.")
        return HttpResponseRedirect("/admin/survey/run")
