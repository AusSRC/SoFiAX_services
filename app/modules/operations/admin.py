"""Admin pages of the operations module: observations, survey components, and the
cross matching and release of sources on the run page."""

import math
import time
import logging
import re
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import ModelForm, forms
from django.shortcuts import redirect
from modules.core.admin.common import RunLinkColumn, link_column
from modules.core.decorators import add_tag_form
from modules.core.models import Detection, Run, TagDetection, ValueTaskReturn, detection_thresholds
from modules.core.utils.base import EditableModelAdmin, ModelAdmin
from modules.core.utils.forms import _get_or_create_tag
from modules.core.utils.task import task
from modules.operations.components import (
    get_release_name,
    get_survey_component_by_name,
    get_survey_component_runs,
    get_survey_components,
)
from modules.operations.constants import RUN_NAME_TO_SURVEY_COMPONENT
from modules.operations.models import ExternalConflict, Observation, SurveyComponent, SurveyComponentRun
from modules.core.admin.runs import RUN_TASKS
from modules.core.admin.runs import RunAdmin as CoreRunAdmin
from modules.operations.signals import detection_released

logging.basicConfig(level=logging.INFO)


class ObservationForm(ModelForm):
    class Meta:
        model = Observation
        fields = "__all__"

    def clean_flags(self):
        """Validate input flags"""
        region_str = self.cleaned_data.get("flags")
        if not region_str:
            return region_str
        try:
            region_list = region_str.split(";")
            for region in region_list:
                x1, x2, y1, y2, z1, z2 = tuple([int(v) for v in region.replace("(", "").replace(")", "").split(",")])
                assert x2 > x1, "x2 > x1"
                assert y2 > y1, "y2 > y1"
                assert z2 > z1, "z2 > z1"
        except Exception:
            raise ValidationError(
                f"Invalid input format. Expected: (x1,x2,y1,y2,z1,z2);(x1,x2,y1,y2,z1,z2);...\n Got: {self.cleaned_data.get('flags')}"
            )
        return region_str


class ObservationAdmin(RunLinkColumn, ModelAdmin):
    form = ObservationForm
    list_display = ["id", "name", "phase", "sbid", "quality", "status", "run_link", "scheduled", "flags"]
    readonly_fields = [
        "id",
        "name",
        "phase",
        "sbid",
        "quality",
        "status",
        "run_link",
        "scheduled",
        "run",
        "ra",
        "dec",
        "rotation",
        "image_cube_file",
        "weights_cube_file",
        "description",
    ]
    list_editable = ["flags"]
    search_fields = ["name", "sbid", "quality", "status", "scheduled"]
    ordering = ("-sbid",)

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        """Show only Full Survey fields that have been observed"""
        qs = super(ObservationAdmin, self).get_queryset(request)
        return qs.filter(phase="Full Survey", sbid__isnull=False)


class SurveyComponentRunInline(admin.TabularInline):
    model = SurveyComponentRun
    extra = 1
    autocomplete_fields = ["run"]

    def formfield_for_dbfield(self, *args, **kwargs):
        formfield = super().formfield_for_dbfield(*args, **kwargs)
        if formfield:
            formfield.widget.can_delete_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_add_related = False
            formfield.widget.can_view_related = True

        return formfield


class SurveyComponentAdmin(EditableModelAdmin):
    inlines = [
        SurveyComponentRunInline,
    ]


class RunAdmin(CoreRunAdmin):
    """Runs with external conflicts, cross matching and the release of sources."""

    list_display = (*CoreRunAdmin.list_display, "run_external_conflicts")
    actions = [
        "_download_summaries",
        "_internal_cross_match",
        "_external_cross_match",
        "_release_sources",
        "_auto_assign_to_component",
        "_delete_run",
    ]

    run_external_conflicts = link_column("external_conflict", "External conflicts", parameter="run_id")

    def _is_match(self, d1, d2, thresh_spat=90.0, thresh_spec=2e6):
        """Check if two detections are a match based on spatial and spectral separation."""
        try:
            ra_i = d1.ra * math.pi / 180.0
            dec_i = d1.dec * math.pi / 180.0
            ra_j = d2.ra * math.pi / 180.0
            dec_j = d2.dec * math.pi / 180.0
            r_spat = (
                3600.0
                * (180.0 / math.pi)
                * math.acos(
                    math.sin(dec_i) * math.sin(dec_j) + math.cos(dec_i) * math.cos(dec_j) * math.cos(ra_i - ra_j)
                )
            )
            r_spec = abs(d1.freq - d2.freq)
        except Exception as e:
            raise Exception(f"Math error {e}")
        if r_spat < thresh_spat and r_spec < thresh_spec:
            return True
        return False

    def auto_assign_run_to_component(self, request, queryset):
        """Auto assign runs to survey components based on the run name."""
        survey_component_runs = get_survey_component_runs()
        for run in queryset:
            if run.name in survey_component_runs:
                messages.error(
                    request,
                    f"Run '{run.name}' already has an existing\
                    survey component.",
                )
                continue
            match_found = False
            for run_pattern in RUN_NAME_TO_SURVEY_COMPONENT:
                if re.match(run_pattern, run.name):
                    match_found = True
                    component_name = RUN_NAME_TO_SURVEY_COMPONENT.get(run_pattern)
                    with transaction.atomic():
                        component = get_survey_component_by_name(component_name)
                        if component:
                            SurveyComponentRun.objects.create(run=run, sc=component)
                            message = f"Successfully auto assigned run '{run.name}' to\
                                survey component '{component.name}'"
                            messages.info(request, message)
                            logging.info(message)
                        else:
                            messages.error(
                                request,
                                f"Unable to auto-assign run '{run.name}' to\
                                survey component '{component_name}'.\
                                Survey component '{component_name}' does not exist.",
                            )
                    # No need to look for another match
                    break
            if match_found is False:
                messages.error(
                    request,
                    f"Run '{run.name}' does not match any known\
                    survey component patterns.",
                )

    def _auto_assign_to_component(self, request, queryset):
        try:
            self.auto_assign_run_to_component(request, queryset)
        except Exception as e:
            messages.error(request, str(e))

    _auto_assign_to_component.short_description = "Auto-assign to Survey Component"

    def _internal_cross_match(self, request, queryset):
        try:
            task_id = self.internal_cross_match(request, queryset)
            logging.info(f"Created task {task_id} for internal cross matching")
            return redirect("/admin/survey/task/")
        except Exception as e:
            messages.error(request, str(e))

    @task(exclusive_func_with=RUN_TASKS)
    def internal_cross_match(self, request, queryset):
        """Run the internal cross matching workflow"""
        if queryset.count() != 1:
            raise Exception("Only one run can be selected at a time for internal cross matching.")

        run = queryset.first()

        with transaction.atomic():
            # This filter is here to lock all the detections
            Detection.objects.filter(run=run).select_for_update()
            all_run_detections = Detection.objects.filter(run=run, unresolved=False, **detection_thresholds())

            if any([d.unresolved for d in all_run_detections]):
                raise Exception(
                    "There cannot be any unresolved detections for the run at the time of running internal cross matching."
                )

            detections = list(Detection.objects.filter(run=run, accepted=True))

            # cross match internally
            logging.info("The following pairs of detections have been marked as unresolved:")
            matches = []
            for i in range(len(detections) - 1):
                for j in range(i + 1, len(detections) - 1):
                    d1 = detections[i]
                    d2 = detections[j]
                    if self._is_match(d1, d2):
                        matches.append((i, j))
                        d1.unresolved = True
                        d1.save()
                        d2.unresolved = True
                        d2.save()
                        logging.info(f"{d1.name}, {d2.name}")

            return ValueTaskReturn(f"Completed internal cross matching for {run.name}")

    _internal_cross_match.short_description = "Internal cross matching"

    @task(exclusive_func_with=RUN_TASKS)
    def external_cross_match(self, request, queryset):
        # Threshold values
        thresh_spat = 90.0
        thresh_spec = 2e6
        thresh_spat_auto = 5.0
        thresh_spec_auto = 0.05e6
        SEARCH_THRESHOLD = 1.0

        if queryset.count() != 1:
            raise Exception("Only one run can be selected at a time for external cross matching.")

        # Check to make sure run is in survey_components
        run = queryset.first()
        survey_component_runs = get_survey_component_runs()

        if run.name not in survey_component_runs:
            raise Exception("This run is not in the survey component list.")

        # Make sure all runs have a survey component
        existing_runs = [r.name for r in Run.objects.all()]
        if set(existing_runs) != set(survey_component_runs):
            diff_runs = list(set(existing_runs) - set(survey_component_runs))
            raise Exception(f"Runs with no survey components: {diff_runs}")

        with transaction.atomic():
            Detection.objects.filter(accepted=True, source_name__isnull=False).select_for_update()

            # Get survey components
            survey_components = get_survey_components()

            run_list = list(queryset)
            if len(run_list) != 1:
                raise Exception("Only one run can be selected at a time for external cross matching.")

            PROJECT = settings.PROJECT

            run = run_list[0]
            run_detections = Detection.objects.filter(
                run=run, accepted=True
            )  # Accepted detections that are not yet sources

            if any([d.unresolved for d in run_detections]):
                raise Exception(
                    "There cannot be any unresolved detections for the run at the time of running external cross matching."
                )

            # Detections from run must enter into one of these lists
            accepted_detections = []
            all_rename_detections = []
            external_conflicts = []

            logging.info(f"External cross matching applied in {run.name} to {len(run_detections)} detections")
            start = time.time()
            for idx, d in enumerate(run_detections):
                auto_rename = False
                auto_delete = False
                matches = []
                delete_detections = []
                rename_detections = []

                # Compare against close detections (accepted) from other runs in the same survey component
                # TODO: Fix this threshold for the poles with delta RA (cosine factor)
                this_sc_id = SurveyComponentRun.objects.get(run=run).sc_id
                sc_run_ids = [scr.run_id for scr in SurveyComponentRun.objects.filter(sc_id=this_sc_id)]
                sc_runs = Run.objects.filter(id__in=sc_run_ids)
                close_detections = Detection.objects.filter(
                    accepted=True,
                    source_name__isnull=False,
                    ra__range=(d.ra - SEARCH_THRESHOLD, d.ra + SEARCH_THRESHOLD),
                    dec__range=(d.dec - SEARCH_THRESHOLD, d.dec + SEARCH_THRESHOLD),
                    run__in=sc_runs,
                ).exclude(run=run)

                for d_ext in list(set(close_detections)):
                    # Require official released source.
                    # TODO: require associated tag?
                    if PROJECT not in d_ext.source_name:
                        continue

                    # Auto-delete check on tighter threshold values
                    if self._is_match(d, d_ext, thresh_spat=thresh_spat_auto, thresh_spec=thresh_spec_auto):
                        # Logic: delete if in same survey component or reassign to existing source otherwise.
                        delete = False
                        for runs in survey_components.values():
                            if set([d.run.name, d_ext.run.name]).issubset(set(runs)):
                                delete = True
                        if delete:
                            auto_delete = True
                            delete_detections.append(d_ext)
                        else:
                            auto_rename = True
                            rename_detections.append((d, d_ext))

                    # Otherwise mark for manual resolution
                    elif self._is_match(d, d_ext, thresh_spat=thresh_spat, thresh_spec=thresh_spec):
                        matches.append(d_ext)

                # Possible action for this detection
                if auto_delete:
                    logging.info(
                        f"[{idx + 1}/{len(run_detections)}] {d.name} to be automatically deleted. Conflict: {delete_detections}"
                    )

                if auto_rename and not auto_delete:
                    if len(rename_detections) > 1:
                        logging.error(f"Multiple rename sources: {rename_detections}")
                        raise Exception(
                            "Should not be able to rename a detection to more than one source (existing database conflict to resolve)."
                        )

                    # Check other detections pointing to rename source in same survey component
                    conflict_in_survey_component = False
                    d_cur, d_ext = rename_detections[0]
                    ds = Detection.objects.filter(source_name=d_ext.source_name)
                    for d in ds:
                        if set([d_cur.run.name, d.run.name]).issubset(set(runs)):
                            conflict_in_survey_component = True
                            logging.info(
                                f"Cannot rename detection {d_cur.name} to {d_ext.source_name} due to potential conflict {d.name} in same survey component."
                            )
                            logging.info(f"Creating external conflict {d_cur.name} to detection {d.name}")
                            external_conflicts.append({"run": run, "detection": d_cur, "conflict_detection": d_ext})
                    if not conflict_in_survey_component:
                        all_rename_detections += rename_detections
                        logging.info(
                            f"[{idx + 1}/{len(run_detections)}] {d.name} to be automatically renamed to {d_ext.source_name} [{d_ext.run.name}]"
                        )

                if not auto_rename and not auto_delete and matches:
                    logging.info(
                        f"[{idx + 1}/{len(run_detections)}] Matches found for {d.name}: {matches} to resolve manually"
                    )
                    for d_ext_match in matches:
                        external_conflicts.append({"run": run, "detection": d, "conflict_detection": d_ext_match})
                if not auto_rename and not auto_delete and not matches:
                    accepted_detections.append(d)
                    logging.info(f"[{idx + 1}/{len(run_detections)}] {d.name} will be accepted")

            end = time.time()
            logging.info(f"External cross matching completed in {round(end - start, 2)} seconds")

            # Release name check for detections in the same survey component
            accepted_source_names = set([get_release_name(d.name) for d in accepted_detections])
            sc_run_ids = [
                scr.run_id
                for scr in SurveyComponentRun.objects.filter(sc_id=SurveyComponentRun.objects.get(run=run).sc_id)
            ]
            sc_runs = Run.objects.filter(id__in=sc_run_ids)
            existing_names = set(
                [
                    d.source_name
                    for d in Detection.objects.filter(
                        accepted=True, source_name__isnull=False, run__in=sc_runs
                    ).exclude(run=run)
                ]
            )
            if accepted_source_names & existing_names:
                logging.error("External cross matching failed - release name already exists for accepted detection.")
                raise Exception(f"Attempting to rename to: {accepted_source_names.intersection(existing_names)}")

            logging.info("Writing updates to database")
            # Accepted sources
            for d in accepted_detections:
                d.source_name = get_release_name(d.name)
                d.save()

            # Renaming
            logging.info(f"Renaming: {all_rename_detections}")
            for d, new_d in all_rename_detections:
                # Check if deleted in this run
                logging.info(f"Database update: Renaming {d.source_name} to {new_d.source_name}")
                d.source_name = new_d.source_name
                d.save()

            # External conflicts
            for ex_c in external_conflicts:
                ExternalConflict.objects.get_or_create(**ex_c)

            logging.info("Updating database complete")
            return ValueTaskReturn(f"Completed {run.name} external cross matching")

    def _external_cross_match(self, request, queryset):
        """Run the external cross matching workflow to identify sources
        that conflict with sources from other survey components.

        """
        try:
            task_id = self.external_cross_match(request, queryset)
            logging.info(f"Created task {task_id} for external cross matching")
            return redirect("/admin/survey/task/")
        except Exception as e:
            messages.error(request, str(e))

    _external_cross_match.short_description = "External cross matching"

    class ReleaseSourceForm(forms.Form):
        title = "Release sources for selected runs. Created source names and adds new tag to all sources."

    @task(exclusive_func_with=["internal_cross_match", "external_cross_match", "release_sources", "delete_run"])
    def release_sources(self, request, queryset, tag):
        with transaction.atomic():
            for run in queryset:
                logging.info(f"Preparing release for run {run.name}")

                detections = (
                    Detection.objects.filter(run=run, accepted=True)
                    .filter(run=run, source_name__isnull=False)
                    .select_for_update()
                )
                release_detections = detections.filter(accepted=True, source_name__isnull=False)
                reject_detections = detections.filter(
                    accepted=True, source_name__isnull=True
                )  # NOTE: there shouldn't be any of these

                if len(ExternalConflict.objects.filter(run_id=run.id)) != 0:
                    raise Exception("There cannot be any external conflicts when creating release source names.")
                if any([d.unresolved for d in release_detections]):
                    raise Exception("There cannot be any unresolved detections when releasing sources.")

                # Release sources
                logging.info(f"{len(release_detections)} detections to release")
                for idx, d in enumerate(release_detections):
                    existing = TagDetection.objects.filter(tag=tag, detection=d)
                    if not existing:
                        logging.info(
                            f"[{idx + 1}/{len(release_detections)}] Creating TagDetection entry for Source {d.source_name}"
                        )
                        TagDetection.objects.create(tag=tag, detection=d, author=str(request.user))
                    else:
                        logging.info(f"Tag already created for Source {d.source_name}")

                    # Other modules can act on the released detection
                    detection_released.send(sender=Detection, detection=d)

                # Delete sources
                logging.info(f"De-selecting remaining detections {len(reject_detections)}")
                for idx, d in enumerate(reject_detections):
                    logging.info(f"[{idx + 1}/{len(reject_detections)}] Rejecting detection {d.name}")
                    d.accepted = None
                    d.save(update_fields=["accepted"])

                logging.info("Release completed")

            names = [run.name for run in queryset]
            return ValueTaskReturn(f"Completed release for {','.join(names)}")

    @add_tag_form(ReleaseSourceForm)
    def _release_sources(self, request, queryset):
        """Create releases for a given run. This will update source names to be
        official release names and create a new tag for all sources.

        Needs for there to be no internal or external conflicts.

        """
        try:
            tag = _get_or_create_tag(request)
            task_id = self.release_sources(request, queryset, tag)
            logging.info(f"Created task {task_id} for releasing sources")
            # TODO: update metadata in data products here...
            # TODO: calculate derived properties (hi_cor, f_sum_cor)

            return redirect("/admin/survey/task/")
        except Exception as e:
            messages.error(request, str(e))
            return

    _release_sources.short_description = "Release sources"


admin.site.register(Observation, ObservationAdmin)
admin.site.register(SurveyComponent, SurveyComponentAdmin)

# The run page of the core module with the additions of this module
admin.site.unregister(Run)
admin.site.register(Run, RunAdmin)
