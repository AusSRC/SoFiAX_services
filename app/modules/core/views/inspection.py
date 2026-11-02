"""Manual inspection of detections (core module)."""

from modules.core.signals import inspection_matches
import logging
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe
from modules.core.models import Detection, Product, Run, Tag, TagDetection, detection_thresholds
from modules.core.utils.forms import _add_comment, _add_tag
from modules.core.utils.plot import product_summary_image
from modules.core.utils.views import handle_navigation, handle_next


logging.basicConfig(level=logging.INFO)


def _inspection_queue(run):
    """Detections of a run that are waiting for manual inspection."""
    return Detection.objects.filter(
        run=run,
        accepted__isnull=True,
        source_name__isnull=True,
        **detection_thresholds(),
    )


# TODO: require superuser status
def manual_inspection_detection_view(request):
    # Handle GET request
    if request.method == "GET":
        run_id = request.GET.get("run_id", None)
        if not run_id:
            raise Exception("Run not selected or does not exist.")
        try:
            run_id = int(run_id)
        except ValueError:
            return HttpResponse("Run id is not an integer.", status=400)

        run = Run.objects.get(id=int(run_id))
        queryset = _inspection_queue(run)

        if len(queryset) == 0:
            messages.info(request, "All detections for this run have been resolved")
            return HttpResponseRedirect("/admin/survey/run")
        detection_id = request.GET.get("detection_id", queryset[0].id)
        detection = Detection.objects.get(id=detection_id)
        idx = list(queryset).index(detection)

        # Show image
        product = Product.objects.get(detection=detection)
        img_src = product_summary_image(product, size=(12, 9))

        ra, dec = detection.equatorial()
        properties = {}
        if ra is not None:
            properties["RA"] = round(ra, 4)
            properties["Dec"] = round(dec, 4)
        if detection.ra is None and detection.l is not None and detection.b is not None:
            properties["Glon"] = round(detection.l, 4)
            properties["Glat"] = round(detection.b, 4)
        properties.update(
            {
                "freq [MHz]": round(detection.freq / 10**6, 2),
                "v_opt": round(299792.458 * (1.42040575e9 / detection.freq - 1.0), 2),
                "f_sum": round(detection.f_sum, 2),
                "rel": None if detection.rel is None else round(detection.rel, 2),
                "rms [mJy]": round(detection.rms * 10**3, 2),
                "snr": round(detection.f_sum / detection.err_f_sum, 2) if detection.err_f_sum else None,
            }
        )

        links = {}
        if ra is not None:
            links = {
                "NED": f"https://ned.ipac.caltech.edu/cgi-bin/objsearch?search_type=Near+Position+Search&in_csys=Equatorial&in_equinox=J2000.0&lon={round(ra, 5)}d&lat={round(dec, 5)}d&radius=0.5",
                "LS-DR10": f"https://www.legacysurvey.org/viewer/jpeg-cutout?layer=ls-dr10&ra={round(ra, 5)}&dec={round(dec, 5)}&pixscale=0.262&size=768",
                "DECaPS": f"https://decaps.legacysurvey.org/viewer/cutout.jpg?layer=decaps2&ra={round(ra, 5)}&dec={round(dec, 5)}&pixscale=0.262&size=768",
            }

        # CARTA button to open the image cube
        carta_url = None
        if settings.CARTA_URL:
            input_data = (detection.instance.parameters or {}).get("input.data")
            if input_data:
                carta_url = f"{settings.CARTA_URL}?file={input_data}"

        # Matches with other catalogues from the installed modules
        matches = {}
        for _, result in inspection_matches.send(sender=Detection, detection=detection):
            matches.update(result or {})

        # Form content
        params = {
            "title": detection.name,
            "subheading": detection.description_string(),
            "subsubheading": f"{idx + 1}/{len(queryset)} detections to resolve.",
            "properties": properties,
            "run_id": run_id,
            "detection_id": detection.id,
            "image": mark_safe(img_src),
            "tags": Tag.objects.all(),
            "links": links,
            "carta_url": carta_url,
            "matches": matches,
        }

        return render(request, "admin/form_inspect_detection.html", params)

    # Handle POST
    elif request.method == "POST":
        body = dict(request.POST)
        run = Run.objects.get(id=int(body["run_id"][0]))
        detection = Detection.objects.get(id=int(body["detection_id"][0]))
        queryset = _inspection_queue(run)
        idx = list(queryset).index(detection)
        url_base = reverse("inspect_detection")
        url_params = f"run_id={run.id}&detection_id="

        action = request.POST.get("action")
        if action in ["Accept", "Reject", "RFI"]:
            with transaction.atomic():
                detection = Detection.objects.select_for_update().get(id=detection.id)
                if action == "Accept":
                    logging.info(f"Marking detection {detection.name} as an accepted detection.")
                    detection.accepted = True
                else:
                    logging.info(f"Rejecting detection {detection.name} ({action}).")
                    detection.accepted = False
                logging.debug(detection.__dict__)
                detection.save(update_fields=["accepted"])

                # RFI is a rejection with the RFI tag
                if action == "RFI":
                    tag, _ = Tag.objects.get_or_create(name="RFI")
                    TagDetection.objects.get_or_create(
                        tag=tag, detection=detection, defaults={"author": str(request.user)}
                    )

                tag_select = request.POST["tag_select"]
                tag_create = str(request.POST["tag_create"])
                if (tag_select != "None") or (tag_create != ""):
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
        return HttpResponseRedirect("/admin/survey/run")
