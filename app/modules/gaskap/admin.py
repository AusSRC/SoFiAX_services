"""Admin pages of the GASKAP-OH module: the columns of the detection lists and the run page."""

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from modules.core.admin.detections import AcceptedDetectionAdmin as CoreAcceptedDetectionAdmin
from modules.core.admin.detections import DetectionAdmin as CoreDetectionAdmin
from modules.core.admin.detections import RejectedDetectionAdmin as CoreRejectedDetectionAdmin
from modules.core.admin.runs import RunAdmin as CoreRunAdmin
from modules.core.models import AcceptedDetection, Detection, RejectedDetection, Run
from modules.gaskap.properties import peak_velocity, rms_mjy, rounded, snr

PEAK_COLUMNS = (
    "display_glong",
    "display_glat",
    "display_f_peak",
    "display_vel_peak",
    "display_vel_range",
    "display_RMS",
    "display_SNR",
)


class PeakColumns:
    """Galactic coordinates and properties at the peak of a detection."""

    # Columns after the properties, when the list is filtered
    extra_columns = ()

    readonly_fields = ("source_name", "name", "tags", "comments", *PEAK_COLUMNS, "detection_products_download")

    @admin.display(description="Glong[deg]")
    def display_glong(self, obj):
        return rounded(obj.l_peak, 4)

    @admin.display(description="Glat[deg]")
    def display_glat(self, obj):
        return rounded(obj.b_peak, 4)

    @admin.display(description="Peak_flux[Jy]")
    def display_f_peak(self, obj):
        return rounded(obj.f_max, 4)

    @admin.display(description="Vel_peak[km/s]")
    def display_vel_peak(self, obj):
        return peak_velocity(obj)

    @admin.display(description="Vel_range[km/s]")
    def display_vel_range(self, obj):
        return peak_velocity(obj)

    @admin.display(description="RMS[mJy]")
    def display_RMS(self, obj):
        return rms_mjy(obj, 4)

    @admin.display(description="SNR")
    def display_SNR(self, obj):
        return snr(obj, 4)

    def get_list_display(self, request):
        if request.GET:
            return (
                "id",
                "summary",
                "run",
                "source_name",
                "name",
                "tags",
                "comments",
                *PEAK_COLUMNS,
                *self.extra_columns,
            )
        return ("id", "run", "name", *PEAK_COLUMNS)


class AcceptedDetectionAdmin(PeakColumns, CoreAcceptedDetectionAdmin):
    extra_columns = ("display_CARTA",)
    readonly_fields = (*PeakColumns.readonly_fields, "display_CARTA")

    @admin.display(description="CARTA")
    def display_CARTA(self, obj):
        input_data = (obj.instance.parameters or {}).get("input.data")
        if not settings.CARTA_URL or not input_data:
            return None
        return format_html("<a href='{}?file={}' target='_blank'>CARTA</a>", settings.CARTA_URL, input_data)


class RejectedDetectionAdmin(PeakColumns, CoreRejectedDetectionAdmin):
    pass


class DetectionAdmin(CoreDetectionAdmin):
    """The detections of a run in galactic coordinates."""

    @admin.display(description="Glong[deg]")
    def display_ra(self, obj):
        return rounded(obj.l, 4)

    @admin.display(description="Glat[deg]")
    def display_dec(self, obj):
        return rounded(obj.b, 4)


class RunAdmin(CoreRunAdmin):
    list_display = (
        "id",
        "name",
        "created",
        "run_accepted_detections",
        "run_rejected_detections",
        "run_manual_inspection",
    )


# The pages of the core module with the changes of this module
for model, model_admin in [
    (AcceptedDetection, AcceptedDetectionAdmin),
    (RejectedDetection, RejectedDetectionAdmin),
    (Detection, DetectionAdmin),
    (Run, RunAdmin),
]:
    admin.site.unregister(model)
    admin.site.register(model, model_admin)
