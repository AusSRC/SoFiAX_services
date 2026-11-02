"""Detections and instances (core module)."""

from django.contrib import admin, messages
from django.db import transaction
from django.forms import forms
from django.shortcuts import redirect
from modules.core.admin.common import (
    DETECTION_COLUMNS,
    DETECTION_HIDDEN_FIELDS,
    DETECTION_IMAGE_COLUMNS,
    DETECTION_ROUNDED_FIELDS,
    DetectionActions,
    DetectionColumns,
    link_column,
    return_to_inspection,
)
from modules.core.decorators import action_form
from modules.core.models import (
    AcceptedDetection,
    Detection,
    Instance,
    RejectedDetection,
    UnresolvedDetection,
    detection_thresholds,
)
from modules.core.tasks import download_accepted_sources, download_accepted_sources_catalog
from modules.core.utils.base import ModelAdmin, ModelAdminInline
from random import choice


class DetectionAdmin(DetectionColumns, DetectionActions, ModelAdmin):
    model = Detection
    list_per_page = 50
    list_display = (
        "id",
        "run",
        "tags",
        "comments",
        "summary",
        "name",
        "display_ra",
        "display_dec",
        "display_freq",
        "display_f_sum",
        "display_v_opt",
        "display_rel",
        "display_rms",
        "display_snr",
    )
    search_fields = ["id", "run__name", "name"]
    actions = ["mark_genuine", "check_action", "add_tag", "add_comment"]

    def get_queryset(self, request):
        qs = super(DetectionAdmin, self).get_queryset(request).select_related("run")
        return qs.filter(unresolved=False)

    class AcceptDetectionAction(forms.Form):
        title = "These detections will be marked as real sources."

    def accept_detection(self, request, queryset):
        try:
            with transaction.atomic():
                detect_list = list(queryset.select_for_update())
                run_set = {detect.run.id for detect in detect_list}
                if len(run_set) > 1:
                    messages.error(request, "Detections from multiple runs selected")
                    return 0

                # Create source and source detection entries
                for d in detect_list:
                    d.accepted = True
                    d.save(update_fields=["accepted"])
                messages.info(request, f"Accepted {len(detect_list)} detections.")
                return
        except Exception as e:
            messages.error(request, str(e))
            return

    accept_detection.short_description = "Accept Detections"

    def lookup_allowed(self, lookup, value, request=None):
        return True


class DetectionAdminInline(DetectionColumns, ModelAdminInline):
    # TODO(austin): probably want to show tags if there are any?
    model = Detection
    readonly_fields = ("name", *DETECTION_COLUMNS, "detection_products_download")
    exclude = DETECTION_ROUNDED_FIELDS + DETECTION_HIDDEN_FIELDS
    fk_name = "run"

    def get_queryset(self, request):
        qs = super(DetectionAdminInline, self).get_queryset(request)
        return qs.filter(unresolved=False, **detection_thresholds())


class UnresolvedDetectionAdmin(DetectionColumns, DetectionActions, ModelAdmin):
    model = UnresolvedDetection
    actions = ["check_action", "resolve_action", "manual_resolve", "add_tag", "add_comment"]

    @admin.display(empty_value="None")
    def source(self, obj):
        return obj.source_name

    def get_list_display(self, request):
        if request.GET:
            return ("id", "source", "tags", "summary", "run", "name", *DETECTION_COLUMNS, *DETECTION_IMAGE_COLUMNS)
        return ("id", "run", "name", *DETECTION_COLUMNS, *DETECTION_IMAGE_COLUMNS)

    def lookup_allowed(self, lookup, value, request=None):
        if lookup is None:
            return True
        elif lookup != "run":
            return False
        return True

    def get_queryset(self, request):
        qs = super(UnresolvedDetectionAdmin, self).get_queryset(request).select_related("run")
        return qs.filter(unresolved=True)

    class ResolveDetectionForm(forms.Form):
        title = 'One random unresolved detection below will marked \
            as "resolved" and the rest deleted.'

    class ChangeUnresolvedFlagDetectionForm(forms.Form):
        title = "Manually change unresolved flag of the following \
            detection(s), you may have duplications."

    @action_form(ResolveDetectionForm)
    def resolve_action(self, request, queryset, form):
        try:
            with transaction.atomic():
                detect_list = list(queryset.select_for_update())
                if len(detect_list) <= 1:
                    messages.error(request, "Can not resolve an empty or single detection")
                    return 0
                run_set = {detect.run.id for detect in detect_list}
                if len(run_set) > 1:
                    messages.error(request, "Detections from multiple runs selected")
                    return 0
                for index, detect_outer in enumerate(detect_list):
                    for detect_inner in detect_list[index + 1 :]:
                        if not detect_outer.is_match(detect_inner):
                            msg = f"Detections {detect_inner.id}, {detect_outer.id} are not in the same spacial and spectral range."  # noqa
                            messages.error(request, msg)
                            return 0
                detect = choice(detect_list)
                detect_list.remove(detect)
                qs = queryset.filter(id__in=[detect.id for detect in detect_list])
                detect.unresolved = False
                # Dont update all the field only the unresolved flag
                # updating all the fields can change the precision
                detect.save(update_fields=["unresolved"])
                qs.delete()
                return len(detect_list)
        except Exception as e:
            messages.error(request, str(e))
            return

    resolve_action.short_description = "Auto Resolve Detections"

    @action_form(ChangeUnresolvedFlagDetectionForm)
    def manual_resolve(self, request, queryset, form):
        with transaction.atomic():
            detect_list = list(queryset.select_for_update())
            for detect in detect_list:
                detect.unresolved = False
                detect.save(update_fields=["unresolved"])
            return len(detect_list)

    manual_resolve.short_description = "Manual Resolve Detections"


class UnresolvedDetectionAdminInline(ModelAdminInline):
    model = UnresolvedDetection
    list_display = ("name", "x", "y", "z", "f_sum", "ell_maj", "ell_min", "w20", "w50")
    exclude = DETECTION_HIDDEN_FIELDS
    readonly_fields = list_display
    ordering = ("x",)
    fk_name = "run"

    def get_queryset(self, request):
        qs = super(UnresolvedDetectionAdminInline, self).get_queryset(request)
        return qs.filter(unresolved=True)


class AcceptedDetectionAdmin(DetectionColumns, ModelAdmin):
    # TODO(austin): probably want to show tags if there are any?
    list_per_page = 50
    model = AcceptedDetection
    readonly_fields = ("source_name", "name", "tags", "comments", *DETECTION_COLUMNS, "detection_products_download")
    exclude = DETECTION_ROUNDED_FIELDS + DETECTION_HIDDEN_FIELDS
    actions = ["deselect", "download_products", "download_catalog"]
    fk_name = "run"
    # Manual inspection outcome of the detections in the list
    inspection_outcome = True

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Deselect detection")
    def deselect(self, request, queryset):
        return return_to_inspection(queryset)

    @admin.action(description="Download Catalog")
    def download_catalog(self, request, queryset):
        download_accepted_sources_catalog(request, queryset)
        return redirect("/admin/survey/task/")

    download_catalog.acts_on_all = True

    @admin.action(description="Download Products")
    def download_products(self, request, queryset):
        download_accepted_sources(request, queryset)
        return redirect("/admin/survey/task/")

    download_products.acts_on_all = True

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("run")
        return qs.filter(accepted=self.inspection_outcome, **detection_thresholds())

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
                *DETECTION_COLUMNS,
                *DETECTION_IMAGE_COLUMNS,
            )
        return ("id", "run", "name", *DETECTION_COLUMNS, *DETECTION_IMAGE_COLUMNS)


class AcceptedDetectionAdminInline(DetectionColumns, ModelAdminInline):
    model = AcceptedDetection
    list_display = (
        "source_name",
        "name",
        "tags",
        "comments",
        "x",
        "y",
        "z",
        "f_sum",
        "ell_maj",
        "ell_min",
        "w20",
        "w50",
        "detection_products_download",
    )
    exclude = DETECTION_HIDDEN_FIELDS
    readonly_fields = list_display
    ordering = ("x",)
    fk_name = "run"

    def get_queryset(self, request):
        qs = super(AcceptedDetectionAdminInline, self).get_queryset(request)
        return qs.filter(accepted=True, unresolved=False, **detection_thresholds())


class RejectedDetectionAdmin(AcceptedDetectionAdmin):
    """Detections rejected in manual inspection (accepted=False)."""

    model = RejectedDetection
    actions = ["reopen", "download_products"]
    inspection_outcome = False

    @admin.action(description="Reopen detection (return to manual inspection)")
    def reopen(self, request, queryset):
        return return_to_inspection(queryset)


class RejectedDetectionAdminInline(AcceptedDetectionAdminInline):
    model = RejectedDetection

    def get_queryset(self, request):
        qs = ModelAdminInline.get_queryset(self, request)
        return qs.filter(accepted=False, **detection_thresholds())


class InstanceColumns:
    """Columns and query shared by the instance admin classes."""

    instance_products_download = link_column("instance_products", "Products")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("run").only("filename", "run", "run_date", "boundary")


class InstanceAdmin(InstanceColumns, ModelAdmin):
    model = Instance
    list_display = ("id", "filename", "run", "run_date", "boundary", "return_code", "instance_products_download")
    fields = (
        "id",
        "filename",
        "version",
        "run",
        "run_date",
        "boundary",
        "parameters",
        "return_code",
        "instance_products_download",
    )
    raw_id_fields = ["run"]


class InstanceAdminInline(InstanceColumns, ModelAdminInline):
    model = Instance
    list_display = ("id", "filename", "run_date", "boundary", "return_code", "version", "instance_products_download")
    exclude = ["parameters"]
    readonly_fields = list_display


admin.site.register(Instance, InstanceAdmin)
admin.site.register(Detection, DetectionAdmin)
admin.site.register(UnresolvedDetection, UnresolvedDetectionAdmin)
admin.site.register(AcceptedDetection, AcceptedDetectionAdmin)
admin.site.register(RejectedDetection, RejectedDetectionAdmin)
