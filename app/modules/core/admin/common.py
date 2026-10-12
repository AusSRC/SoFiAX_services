"""Columns, links and actions shared by the admin classes."""

import logging
from django.contrib import admin, messages
from django.db import transaction
from django.forms import forms
from django.urls import reverse
from django.utils.html import format_html
from modules.core.decorators import add_comment_form, add_tag_form
from modules.core.models import Comment, TagDetection
from modules.core.utils.forms import _add_comment, _get_or_create_tag


logging.basicConfig(level=logging.INFO)


def sanity_check(request, queryset):
    try:
        detect_list = list(queryset)
        for index, detect_outer in enumerate(detect_list):
            for detect_inner in detect_list[index + 1 :]:
                logging.info(f"Detections: {detect_outer.id}, {detect_inner.id}")
                if detect_outer.is_match(detect_inner):
                    logging.info("Passed is_match test")
                    sanity, msg = detect_outer.sanity_check(detect_inner)
                    if sanity is False:
                        logging.info("Sanity check has failed")
                        messages.error(request, msg)
                    else:
                        logging.info("Passed sanity_check test")
                        messages.info(request, "sanity passed")
                else:
                    # TODO(austin): could probably keep both of these sources if not match...
                    msg = f"Detections {detect_inner.id}, {detect_outer.id} are not in the same spacial and spectral range"  # noqa
                    messages.error(request, msg)
    except Exception as e:
        messages.error(request, str(e))


def render_summary(obj):
    """Summary plot of a detection with a link to the full size version."""
    img = obj.summary_image()
    if img is None:
        return None
    url = reverse("summary_image")
    if img.startswith("<img"):
        return format_html("<a href='{}?id={}' target='_blank'>{}</a>", url, obj.id, img)
    # HTML plots are interactive, so the link is separate from the plot
    return format_html("<div>{}</div><a href='{}?id={}' target='_blank'>Open full size</a>", img, url, obj.id)


def link_column(view, label, description=None, parameter="id"):
    """Admin column with a link to a view for the object."""

    @admin.display(description=description or label)
    def column(self, obj):
        return format_html("<a href='{}?{}={}'>{}</a>", reverse(view), parameter, obj.id, label)

    return column


def run_changelist_column(model_name, label):
    """Admin column for a run with a link to a detection list filtered to the run."""

    @admin.display(description=label)
    def column(self, obj):
        url = reverse(f"admin:{self.model._meta.app_label}_{model_name}_changelist")
        return format_html("<a href='{}?run={}'>{}</a>", url, obj.id, label)

    return column


def rounded_column(field, description=None):
    """Admin column with the rounded value of a field."""

    @admin.display(description=description or field)
    def column(self, obj):
        value = getattr(obj, field)
        return None if value is None else round(value, 4)

    return column


def return_to_inspection(queryset):
    """Clear the manual inspection outcome of the detections."""
    with transaction.atomic():
        for d in queryset:
            d.accepted = None
            d.save(update_fields=["accepted"])
    return len(queryset)


# Detection fields shown as rounded columns in the lists
DETECTION_COLUMNS = (
    "display_x",
    "display_y",
    "display_z",
    "display_f_sum",
    "display_ell_maj",
    "display_ell_min",
    "display_w20",
    "display_w50",
)


DETECTION_IMAGE_COLUMNS = ("moment0_image", "spectrum_image")


# Detection fields that are not shown on the detail pages
DETECTION_HIDDEN_FIELDS = [
    "x_peak",
    "y_peak",
    "z_peak",
    "ra_peak",
    "dec_peak",
    "freq_peak",
    "b_peak",
    "l_peak",
    "v_rad_peak",
    "v_opt_peak",
    "v_app_peak",
    "x_min",
    "x_max",
    "y_min",
    "y_max",
    "z_min",
    "z_max",
    "n_pix",
    "f_min",
    "f_max",
    "rel",
    "rms",
    "ell_pa",
    "ell3s_maj",
    "ell3s_min",
    "ell3s_pa",
    "kin_pa",
    "err_x",
    "err_y",
    "err_z",
    "err_f_sum",
    "ra",
    "dec",
    "freq",
    "flag",
    "unresolved",
    "instance",
    "l",
    "b",
    "v_rad",
    "v_opt",
    "v_app",
]


# Fields replaced by their rounded columns
DETECTION_ROUNDED_FIELDS = ["x", "y", "z", "f_sum", "ell_min", "ell_maj", "w20", "w50", "wm50"]


class DetectionColumns:
    """Columns shared by the detection admin classes."""

    display_x = rounded_column("x")
    display_y = rounded_column("y")
    display_z = rounded_column("z")
    display_f_sum = rounded_column("f_sum", "f sum")
    display_ell_maj = rounded_column("ell_maj", "ell maj")
    display_ell_min = rounded_column("ell_min", "ell min")
    display_w20 = rounded_column("w20")
    display_w50 = rounded_column("w50")
    display_freq = rounded_column("freq")
    display_rel = rounded_column("rel")
    display_rms = rounded_column("rms")
    detection_products_download = link_column("detection_products", "Products")

    @admin.display(description="RA")
    def display_ra(self, obj):
        ra, dec = obj.equatorial()
        return None if ra is None else round(ra, 4)

    @admin.display(description="Dec")
    def display_dec(self, obj):
        ra, dec = obj.equatorial()
        return None if dec is None else round(dec, 4)

    @admin.display(description="v_opt")
    def display_v_opt(self, obj):
        return round(299792.458 * (1.42040575e9 / obj.freq - 1.0), 4)

    @admin.display(description="snr")
    def display_snr(self, obj):
        if (obj.err_f_sum is None) or (obj.f_sum is None):
            return None
        return round(obj.f_sum / obj.err_f_sum, 4)

    def tags(self, obj):
        return ", ".join(td.tag.name for td in TagDetection.objects.filter(detection=obj)) or "-"

    def comments(self, obj):
        return ", ".join(c.comment for c in Comment.objects.filter(detection=obj)) or "-"

    @admin.display(empty_value=None)
    def summary(self, obj):
        return render_summary(obj)


class DetectionActions:
    """Actions shared by the detection admin classes."""

    @admin.action(description="Sanity Check Detections")
    def check_action(self, request, queryset):
        sanity_check(request, queryset)

    class AddTagForm(forms.Form):
        title = "Add tags"

    @add_tag_form(AddTagForm)
    def add_tag(self, request, queryset):
        with transaction.atomic():
            # The tag is created once for all of the detections
            tag = _get_or_create_tag(request)
            for d in queryset:
                TagDetection.objects.get_or_create(tag=tag, detection=d, defaults={"author": str(request.user)})
        return len(queryset)

    add_tag.short_description = "Add tags"

    class AddCommentForm(forms.Form):
        title = "Add comments"

    @add_comment_form(AddCommentForm)
    def add_comment(self, request, queryset):
        with transaction.atomic():
            for d in queryset:
                _add_comment(request, d)
        return len(queryset)

    add_comment.short_description = "Add comments"


class RunLinkColumn:
    """Column with a link to the run of an object."""

    @admin.display(description="Run")
    def run_link(self, obj):
        if not obj.run:
            return "-"
        url = reverse("admin:survey_run_changelist")
        return format_html("<a href='{}?q={}'>{}</a>", url, obj.run.name, obj.run.name)
