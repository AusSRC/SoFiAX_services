"""Runs (core module). Other modules add columns and actions by registering a subclass of RunAdmin."""

import logging
from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import redirect
from modules.core.admin.common import link_column, run_changelist_column
from modules.core.admin.detections import (
    AcceptedDetectionAdminInline,
    DetectionAdminInline,
    InstanceAdminInline,
    RejectedDetectionAdminInline,
    UnresolvedDetectionAdminInline,
)
from modules.core.decorators import require_confirmation
from modules.core.models import Run, ValueTaskReturn
from modules.core.tasks import download_summaries_for_run
from modules.core.utils.base import ModelAdmin
from modules.core.utils.task import task

logging.basicConfig(level=logging.INFO)


# Tasks on runs that cannot run at the same time
RUN_TASKS = ["internal_cross_match", "external_cross_match", "release_sources", "delete_run", "download_summaries"]


class RunAdmin(ModelAdmin):
    model = Run
    list_display = (
        "id",
        "name",
        "created",
        "sanity_thresholds",
        "run_unresolved_detections",
        "run_accepted_detections",
        "run_rejected_detections",
        "run_manual_inspection",
    )
    actions = ["_download_summaries", "_delete_run"]
    inlines = (
        UnresolvedDetectionAdminInline,
        AcceptedDetectionAdminInline,
        RejectedDetectionAdminInline,
        DetectionAdminInline,
        InstanceAdminInline,
    )

    ordering = ("-created",)

    search_fields = ["name"]

    def has_delete_permission(self, request, obj=None):
        return False

    run_products_download = link_column("run_products", "Products")

    run_catalog = link_column("run_catalog", "Catalog")

    run_unresolved_detections = run_changelist_column("unresolveddetection", "Unresolved Detections")

    run_accepted_detections = run_changelist_column("accepteddetection", "Accepted Detections")

    run_rejected_detections = run_changelist_column("rejecteddetection", "Rejected Detections")

    run_manual_inspection = link_column("inspect_detection", "Manual inspection", parameter="run_id")

    @task(exclusive_func_with=RUN_TASKS)
    def download_summaries(self, request, queryset):
        try:
            return download_summaries_for_run(request, queryset)
        except Exception as e:
            messages.error(request, str(e))

    def _download_summaries(self, request, queryset):
        try:
            if queryset.count() == 0:
                messages.error(request, "No Run(s) selected")
                return

            self.download_summaries(request, queryset)
            return redirect("/admin/survey/task/")
        except Exception as e:
            messages.error(request, str(e))

    _download_summaries.short_description = "Download Summaries"

    @task(exclusive_func_with=RUN_TASKS)
    def delete_run(self, request, queryset):
        names = [i.name for i in queryset]
        with transaction.atomic():
            queryset._raw_delete(queryset.db)
        return ValueTaskReturn(f"Run(s) deleted: {names}")

    @require_confirmation
    def _delete_run(self, request, queryset):
        try:
            if queryset.count() == 0:
                messages.error(request, "No Run(s) selected")
                return

            self.delete_run(request, queryset)
            return redirect("/admin/survey/task/")
        except Exception as e:
            messages.error(request, str(e))

    _delete_run.short_description = "Delete Run"


admin.site.register(Run, RunAdmin)
