import re
import math
import time
import logging
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.forms import forms
from django.db import transaction
from random import choice

from survey.utils.base import ModelAdmin, ModelAdminInline
from survey.decorators import action_form, add_tag_form, add_comment_form
from survey.models import Detection, UnresolvedDetection, ExternalConflict,\
    Source, Instance, Run, SourceDetection, Comment, Tag, TagSourceDetection, KinematicModel


logging.basicConfig(level=logging.INFO)


class TagAdmin(ModelAdmin):
    list_display = ('name', 'description', 'added_at')

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class TagSourceDetectionAdmin(ModelAdmin):
    list_display = ('tag', 'get_source', 'get_detection', 'author', 'added_at')

    def get_source(self, obj):
        return obj.source_detection.source.name
    get_source.short_description = 'Source'

    def get_detection(self, obj):
        return obj.source_detection.detection.name
    get_detection.short_description = 'Detection'

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if obj.author is None:
            obj.author = request.user
        super().save_model(request, obj, form, change)


class CommentAdmin(ModelAdmin):
    list_display = ('comment', 'detection', 'author', 'updated_at')

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if obj.author is None:
            obj.author = request.user
        super().save_model(request, obj, form, change)


class KinematicModelAdmin(ModelAdmin):
    list_display = [f.name for f in KinematicModel._meta.get_fields()]


class SourceDetectionAdmin(ModelAdmin):
    list_display = ('source', 'detection', 'added_at')


class DetectionAdmin(ModelAdmin):
    model = Detection
    list_per_page = 10
    list_display = ('id', 'source', 'run', 'name', 'x', 'y', 'z',
                    'f_sum', 'ell_maj', 'ell_min', 'w20', 'w50',
                    'detection_products_download')
    search_fields = ['run__name', 'name']
    actions = ['mark_genuine', 'add_tag', 'add_comment']

    @admin.display(empty_value='No')
    def source(self, obj):
        sd = SourceDetection.objects.filter(detection=obj)
        if len(sd) == 1:
            return 'Yes'
        return 'No'

    @admin.display(empty_value=None)
    def tags(self, obj):
        sd = SourceDetection.objects.filter(detection=obj)
        if len(sd) == 1:
            tag_sd = TagSourceDetection.objects.filter(source_detection=sd[0])
            tags = Tag.objects.filter(id__in=[tsd.tag_id for tsd in tag_sd])
            if len(tags) > 0:
                tag_string = ', '.join([t.name for t in tags])
                return tag_string

    @admin.display(empty_value=None)
    def summary(self, obj):
        url = reverse('summary_image')
        return format_html(f"<a href='{url}?id={obj.id}' target='_blank'>{obj.summary_image()}</a>")

    def get_actions(self, request):
        return super(DetectionAdmin, self).get_actions(request)

    def get_list_display(self, request):
        if request.GET:
            return 'id', 'run', 'source', 'tags', 'summary', 'name', 'x', 'y', 'z', 'f_sum', 'ell_maj', 'ell_min',\
                   'w20', 'w50'
        else:
            return 'id', 'run', 'name', 'x', 'y', 'z', 'f_sum', 'ell_maj',\
                   'ell_min', 'w20', 'w50'

    def detection_products_download(self, obj):
        url = reverse('detection_products')
        return format_html(f"<a href='{url}?id={obj.id}'>Products</a>")

    detection_products_download.short_description = 'Products'

    def get_queryset(self, request):
        qs = super(DetectionAdmin, self).\
            get_queryset(request).\
            select_related('run')
        return qs.filter(unresolved=False)

    class MarkGenuineDetectionAction(forms.Form):
        title = 'These detections will be marked as real sources.'

    def mark_genuine(self, request, queryset):
        try:
            with transaction.atomic():
                detect_list = list(queryset.select_for_update())
                run_set = {detect.run.id for detect in detect_list}
                if len(run_set) > 1:
                    messages.error(
                        request,
                        "Detections from multiple runs selected"
                    )
                    return 0

                # Create source and source detection entries
                for detection in detect_list:
                    source = Source.objects.create(name=detection.name)
                    source_detection = SourceDetection.objects.create(
                        source=source,
                        detection=detection
                    )
                messages.info(request, f"Marked {len(detect_list)} detections as sources.")
                return
        except Exception as e:
            messages.error(request, str(e))
            return
    mark_genuine.short_description = 'Mark Genuine Detections'

    class AddTagForm(forms.Form):
        title = 'Add tags'

    @add_tag_form(AddTagForm)
    def add_tag(self, request, queryset):
        try:
            # get or create tag
            tag_select = request.POST['tag_select']
            tag_create = str(request.POST['tag_create'])
            if tag_select == 'None':
                if tag_create == '':
                    messages.error(request, "No tag selected or created")
                    return
                else:
                    tag = Tag.objects.create(
                        name=tag_create
                    )
            else:
                tag = Tag.objects.get(id=int(tag_select))
            detect_list = list(queryset)
            for d in detect_list:
                source_detection = SourceDetection.objects.get(detection=d)
                TagSourceDetection.objects.create(
                    source_detection=source_detection,
                    tag=tag,
                    author=str(request.user)
                )
            return len(detect_list)
        except Exception as e:
            messages.error(request, str(e))
            return
    add_tag.short_description = 'Add tags'

    class AddCommentForm(forms.Form):
        title = 'Add comments'

    @add_comment_form(AddCommentForm)
    def add_comment(self, request, queryset):
        try:
            detect_list = list(queryset)
            comment = str(request.POST['comment'])
            for d in detect_list:
                Comment.objects.create(
                    comment=comment,
                    author=str(request.user),
                    detection=d
                )
            return len(detect_list)
        except Exception as e:
            messages.error(request, str(e))
            return
    add_comment.short_description = 'Add comments'


class DetectionAdminInline(ModelAdminInline):
    # TODO(austin): probably want to show tags if there are any?
    model = Detection
    list_display = (
        'name', 'x', 'y', 'z', 'f_sum',
        'ell_maj', 'ell_min', 'w20', 'w50', 'detection_products_download'
    )
    exclude = [
        'x_peak', 'y_peak', 'z_peak', 'ra_peak', 'dec_peak', 'freq_peak',
        'b_peak', 'l_peak', 'v_rad_peak', 'v_opt_peak', 'v_app_peak',
        'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max', 'n_pix', 'f_min',
        'f_max', 'rel', 'rms', 'ell_pa', 'ell3s_maj', 'ell3s_min', 'ell3s_pa',
        'kin_pa', 'err_x', 'err_y', 'err_z', 'err_f_sum', 'ra', 'dec', 'freq',
        'flag', 'unresolved', 'instance', 'l', 'b', 'v_rad', 'v_opt', 'v_app'
    ]
    readonly_fields = list_display
    fk_name = 'run'

    def detection_products_download(self, obj):
        url = reverse('detection_products')
        return format_html(f"<a href='{url}?id={obj.id}'>Products</a>")

    detection_products_download.short_description = 'Products'

    def get_queryset(self, request):
        qs = super(DetectionAdminInline, self).get_queryset(request)
        return qs.filter(unresolved=False)


class UnresolvedDetectionAdmin(ModelAdmin):
    model = UnresolvedDetection
    actions = ['check_action', 'resolve_action', 'manual_resolve', 'add_tag', 'add_comment']

    @admin.display(empty_value='No')
    def source(self, obj):
        sd = SourceDetection.objects.filter(detection=obj)
        if len(sd) == 1:
            return 'Yes'
        return 'No'

    @admin.display(empty_value=None)
    def tags(self, obj):
        sd = SourceDetection.objects.filter(detection=obj)
        if len(sd) == 1:
            tag_sd = TagSourceDetection.objects.filter(source_detection=sd[0])
            tags = Tag.objects.filter(id__in=[tsd.tag_id for tsd in tag_sd])
            if len(tags) > 0:
                tag_string = ', '.join([t.name for t in tags])
                return tag_string

    @admin.display(empty_value=None)
    def summary(self, obj):
        url = reverse('summary_image')
        return format_html(f"<a href='{url}?id={obj.id}' target='_blank'>{obj.summary_image()}</a>")

    def get_actions(self, request):
        return super(UnresolvedDetectionAdmin, self).get_actions(request)

    def get_list_display(self, request):
        if request.GET:
            return 'id', 'source', 'tags', 'summary', 'run', 'name', 'x', 'y', 'z', 'f_sum', 'ell_maj', 'ell_min',\
                   'w20', 'w50', 'moment0_image', 'spectrum_image'
        else:
            return 'id', 'run', 'name', 'x', 'y', 'z', 'f_sum', 'ell_maj',\
                   'ell_min', 'w20', 'w50', 'moment0_image', 'spectrum_image'

    def lookup_allowed(self, lookup, value):
        if lookup is None:
            return True
        elif lookup != 'run':
            return False
        return True

    def get_queryset(self, request):
        qs = super(UnresolvedDetectionAdmin, self)\
            .get_queryset(request)\
            .select_related('run')
        return qs.filter(unresolved=True)

    class ResolveDetectionForm(forms.Form):
        title = 'One random unresolved detection below will marked \
            as "resolved" and the rest deleted.'

    class ChangeUnresolvedFlagDetectionForm(forms.Form):
        title = 'Manually change unresolved flag of the following \
            detection(s), you may have duplications.'

    @action_form(ResolveDetectionForm)
    def resolve_action(self, request, queryset, form):
        try:
            with transaction.atomic():
                detect_list = list(queryset.select_for_update())
                if len(detect_list) <= 1:
                    messages.error(
                        request,
                        "Can not resolve an empty or single detection"
                    )
                    return 0
                run_set = {detect.run.id for detect in detect_list}
                if len(run_set) > 1:
                    messages.error(
                        request,
                        "Detections from multiple runs selected"
                    )
                    return 0
                for index, detect_outer in enumerate(detect_list):
                    for detect_inner in detect_list[index + 1:]:
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

    resolve_action.short_description = 'Auto Resolve Detections'

    @action_form(ChangeUnresolvedFlagDetectionForm)
    def manual_resolve(self, request, queryset, form):
        with transaction.atomic():
            detect_list = list(queryset.select_for_update())
            for detect in detect_list:
                detect.unresolved = False
                detect.save(update_fields=["unresolved"])
            return len(detect_list)

    manual_resolve.short_description = "Manual Resolve Detections"

    def check_action(self, request, queryset):
        try:
            detect_list = list(queryset)
            for index, detect_outer in enumerate(detect_list):
                for detect_inner in detect_list[index + 1:]:
                    logging.info(f'Detections: {detect_outer.id}, {detect_inner.id}')
                    if detect_outer.is_match(detect_inner):
                        logging.info('Passed is_match test')
                        sanity, msg = detect_outer.sanity_check(detect_inner)
                        if sanity is False:
                            logging.info('Sanity check has failed')
                            messages.error(request, msg)
                        else:
                            logging.info('Passed sanity_check test')
                            messages.info(request, "sanity passed")
                        return
                    else:
                        # TODO(austin): could probably keep both of these sources if not match...
                        msg = f"Detections {detect_inner.id}, {detect_outer.id} are not in the same spacial and spectral range"  # noqa
                        messages.error(request, msg)
                        return
            return None
        except Exception as e:
            messages.error(request, str(e))
            return
    check_action.short_description = 'Sanity Check Detections'

    class AddTagForm(forms.Form):
        title = 'Add tags'

    @add_tag_form(AddTagForm)
    def add_tag(self, request, queryset):
        try:
            # get or create tag
            tag_select = request.POST['tag_select']
            tag_create = str(request.POST['tag_create'])
            if tag_select == 'None':
                if tag_create == '':
                    messages.error(request, "No tag selected or created")
                    return
                else:
                    tag = Tag.objects.create(
                        name=tag_create
                    )
            else:
                tag = Tag.objects.get(id=int(tag_select))
            detect_list = list(queryset)
            for d in detect_list:
                source_detection = SourceDetection.objects.get(detection=d)
                TagSourceDetection.objects.create(
                    source_detection=source_detection,
                    tag=tag,
                    author=str(request.user)
                )
            return len(detect_list)
        except Exception as e:
            messages.error(request, str(e))
            return
    add_tag.short_description = 'Add tags'

    class AddCommentForm(forms.Form):
        title = 'Add comments'

    @add_comment_form(AddCommentForm)
    def add_comment(self, request, queryset):
        try:
            detect_list = list(queryset)
            comment = str(request.POST['comment'])
            for d in detect_list:
                Comment.objects.create(
                    comment=comment,
                    author=str(request.user),
                    detection=d
                )
            return len(detect_list)
        except Exception as e:
            messages.error(request, str(e))
            return
    add_comment.short_description = 'Add comments'


class UnresolvedDetectionAdminInline(ModelAdminInline):
    model = UnresolvedDetection
    list_display = (
        'name', 'x', 'y', 'z', 'f_sum', 'ell_maj', 'ell_min', 'w20', 'w50'
    )
    exclude = [
        'x_peak', 'y_peak', 'z_peak', 'ra_peak', 'dec_peak', 'freq_peak',
        'b_peak', 'l_peak', 'v_rad_peak', 'v_opt_peak', 'v_app_peak',
        'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max', 'n_pix', 'f_min',
        'f_max', 'rel', 'rms', 'ell_pa', 'ell3s_maj', 'ell3s_min', 'ell3s_pa',
        'kin_pa', 'err_x', 'err_y', 'err_z', 'err_f_sum', 'ra', 'dec', 'freq',
        'flag', 'unresolved', 'instance', 'l', 'b', 'v_rad', 'v_opt', 'v_app'
    ]
    readonly_fields = list_display
    ordering = ('x',)
    fk_name = 'run'

    def get_queryset(self, request):
        qs = super(UnresolvedDetectionAdminInline, self).get_queryset(request)
        return qs.filter(unresolved=True)


class InstanceAdmin(ModelAdmin):
    model = Instance
    list_display = (
        'id', 'filename', 'run', 'run_date', 'boundary', 'return_code',
        'instance_products_download'
    )
    fields = (
        'id', 'filename', 'version', 'run', 'run_date', 'boundary',
        'parameters', 'return_code', 'instance_products_download'
    )
    raw_id_fields = ['run']

    def get_queryset(self, request):
        qs = super(InstanceAdmin, self)\
            .get_queryset(request)\
            .select_related('run').\
            only('filename', 'run', 'run_date', 'boundary')
        return qs

    def instance_products_download(self, obj):
        url = reverse('instance_products')
        return format_html(f"<a href='{url}?id={obj.id}'>Products</a>")

    instance_products_download.short_description = 'Products'


class InstanceAdminInline(ModelAdminInline):
    model = Instance
    list_display = (
        'id', 'filename', 'run_date', 'boundary', 'return_code', 'version',
        'instance_products_download'
    )
    exclude = ['parameters']
    readonly_fields = list_display

    def get_queryset(self, request):
        qs = super(InstanceAdminInline, self)\
            .get_queryset(request)\
            .select_related('run').\
            only('filename', 'run', 'run_date', 'boundary')
        return qs

    def instance_products_download(self, obj):
        url = reverse('instance_products')
        return format_html(f"<a href='{url}?id={obj.id}'>Products</a>")

    instance_products_download.short_description = 'Products'


class RunAdmin(ModelAdmin):
    model = Run
    list_display = (
        'id', 'name', 'sanity_thresholds',
        'run_catalog', 'run_link', 'run_products_download',
        'run_manual_inspection', 'external_conflicts'
    )
    inlines = (
        UnresolvedDetectionAdminInline,
        DetectionAdminInline,
        InstanceAdminInline,
    )
    actions = ['internal_cross_match', 'external_cross_match', 'release_sources']

    def get_actions(self, request):
        return super(RunAdmin, self).get_actions(request)

    def run_products_download(self, obj):
        url = reverse('run_products')
        return format_html(f"<a href='{url}?id={obj.id}'>Products</a>")
    run_products_download.short_description = 'Products'

    def run_catalog(self, obj):
        url = reverse('run_catalog')
        return format_html(f"<a href='{url}?id={obj.id}'>Catalog</a>")
    run_catalog.short_description = 'Catalog'

    def run_link(self, obj):
        opts = self.model._meta
        url = reverse(f'admin:{opts.app_label}_unresolveddetection_changelist')
        return format_html(f"<a href='{url}?run={obj.id}'>View</a>")
    run_link.short_description = 'Unresolved Detections'

    def run_manual_inspection(self, obj):
        opts = self.model._meta
        url = reverse(f'admin:{opts.app_label}_detection_changelist')
        return format_html(f"<a href='{url}?run={obj.id}'>Detections</a>")
    run_manual_inspection.short_description = 'Manual inspection'

    def external_conflicts(self, obj):
        opts = self.model._meta
        url = reverse(f'admin:{opts.app_label}_externalconflict_changelist')
        return format_html(f"<a href='{url}?run={obj.id}'>Conflicts</a>")
    external_conflicts.short_description = 'External conflicts'

    def _is_match(self, d1, d2, thresh_spat=90.0, thresh_spec=2e+6):
        """Check if two detections are a match based on spatial and spectral separation.

        """
        ra_i = d1.ra * math.pi / 180.0
        dec_i = d1.dec * math.pi / 180.0
        ra_j = d2.ra * math.pi / 180.0
        dec_j = d2.dec * math.pi / 180.0
        r_spat = 3600.0 * (180.0 / math.pi) * math.acos(math.sin(dec_i) * math.sin(dec_j) + math.cos(dec_i) * math.cos(dec_j) * math.cos(ra_i - ra_j))
        if r_spat < thresh_spat and abs(d1.freq - d2.freq) < thresh_spec:
            return True
        return False

    def internal_cross_match(self, request, queryset):
        """Run the internal cross matching workflow

        """
        try:
            run_list = list(queryset)
            if len(run_list) != 1:
                messages.error(
                    request,
                    "Only one run can be selected at a time for internal cross matching."
                )
                return 0
            run = run_list[0]
            all_run_detections = list(Detection.objects.filter(run=run))

            if any([d.unresolved for d in all_run_detections]):
                messages.error(
                    request,
                    'There cannot be any unresolved detections for the run at the time of running internal cross matching.'
                )
                return 0

            sd_list = list(SourceDetection.objects.filter(detection_id__in=[d.id for d in all_run_detections]))
            detections = [Detection.objects.get(id=sd.detection.id) for sd in sd_list]
            sources = [Source.objects.get(id=sd.source.id) for sd in sd_list]

            # cross match internally
            logging.info('The following pairs of detections have been marked as unresolved:')
            matches = []
            for i in range(len(detections) - 1):
                for j in range(i + 1, len(detections) - 1):
                    d1 = detections[i]
                    d2 = detections[j]
                    if self._is_match(d1, d2):
                        matches.append((i, j))
                        d1 = detections[i]
                        d1.unresolved = True
                        d1.save()
                        d2.unresolved = True
                        d2.save()
                        logging.info(f'{d1.name}, {d2.name}')
            messages.info(request, 'Completed internal cross matching')
            return None
        except Exception as e:
            messages.error(request, str(e))
            return
    internal_cross_match.short_description = 'Internal cross matching'

    def external_cross_match(self, request, queryset):
        """Run the external cross matching workflow to identify sources
        that conflict with sources from other survey components.

        NOTE: current external matching looks forward and backward in time (potentially need
        to ignore the external matches that are more recent than the first detection)

        """
        SEARCH_THRESHOLD = 1.0

        try:
            run_list = list(queryset)
            run = run_list[0]
            run_detections = Detection.objects.filter(
                run=run,
                id__in=[sd.detection_id for sd in SourceDetection.objects.all()]
            )
            if len(run_list) != 1:
                messages.error(
                    request,
                    "Only one run can be selected at a time for internal cross matching."
                )
                return 0
            if any([d.unresolved for d in run_detections]):
                messages.error(
                    request,
                    'There cannot be any unresolved detections for the run at the time of running internal cross matching.'
                )
                return 0

            # Measure external cross matching duration
            start = time.time()
            for d in run_detections:
                close_detections = Detection.objects.filter(
                    id__in=[sd.detection_id for sd in SourceDetection.objects.all()],
                    ra__range=(d.ra - SEARCH_THRESHOLD, d.ra + SEARCH_THRESHOLD),
                    dec__range=(d.dec - SEARCH_THRESHOLD, d.dec + SEARCH_THRESHOLD),
                ).exclude(
                    run=run
                )
                matches = []
                for d_ext in close_detections:
                    if self._is_match(d, d_ext):
                        matches.append(SourceDetection.objects.get(detection=d_ext).id)
                if matches:
                    ExternalConflict.objects.get_or_create(
                        run=run,
                        detection=d,
                        conflict_source_detection_ids=matches
                    )
            end = time.time()
            logging.info("External cross matching duration:", end-start)
            messages.info(request, 'Completed external cross matching')
            return None
        except Exception as e:
            messages.error(request, str(e))
            return
    external_cross_match.short_description = 'External cross matching'

    class ReleaseSourceForm(forms.Form):
        title = 'Release sources for selected runs. Created WALLABY source names and adds new tag to all sources.'

    def _release_name(self, name):
        """Release name from detection name

        """
        parts = re.split('[+-]', name.replace('SoFiA', 'WALLABY'))
        return re.search('[+-]', name).group().join(
            list(map(lambda x: x.split('.')[0], parts))
        )

    @add_tag_form(ReleaseSourceForm)
    def release_sources(self, request, queryset):
        """Create releases for a given run. This will update source names to be
        official WALLABY release names and create a new tag for all sources.

        Needs for there to be no internal or external conflicts.

        """
        try:
            # Get or create tag
            tag_select = request.POST['tag_select']
            tag_create = str(request.POST['tag_create'])
            if tag_select == 'None':
                if tag_create == '':
                    messages.error(request, "No tag selected or created")
                    return
                else:
                    tag = Tag.objects.create(
                        name=tag_create
                    )
                    pass
            else:
                tag = Tag.objects.get(id=int(tag_select))

            for run in queryset:
                logging.info(f"Preparing release for run {run.name}")
                run_detections = Detection.objects.filter(run=run)
                if any([d.unresolved for d in run_detections]):
                    messages.error(
                        request,
                        'There cannot be any unresolved detections when creating release source names.'
                    )
                    return 0
                if len(ExternalConflict.objects.filter(run_id=run.id)) != 0:
                    messages.error(
                        request,
                        'There cannot be any external conflicts when creating release source names.'
                    )
                    return 0

                # Updating source names and tagging
                run_source_detections = SourceDetection.objects.filter(detection_id__in=[d.id for d in run_detections])
                for sd in run_source_detections:
                    TagSourceDetection.objects.create(
                        tag=tag,
                        source_detection=sd
                    )
                    source = sd.source
                    new_name = self._release_name(source.name)
                    logging.info(f"Replacing source name {source.name} -> {new_name}")
                    source.name = new_name
                    source.save()
            return len(queryset)
        except Exception as e:
            messages.error(request, str(e))
            return
    release_sources.short_description = 'Release sources'


class RunAdminInline(ModelAdminInline):
    model = Run
    list_display = ['id', 'name', 'sanity_thresholds', 'run_products_download']
    fields = list_display
    readonly_fields = fields

    def run_products_download(self, obj):
        url = reverse('run_products')
        return format_html(f"<a href='{url}?id={obj.id}'>Products</a>")

    run_products_download.short_description = 'Products'


class ExternalConflictAdmin(ModelAdmin):
    model = ExternalConflict
    list_display = ['id', 'detection_name', 'summary', 'description', 'compare']
    actions = ['add_to_existing_source', 'delete_new_source', 'add_tag', 'add_comment']

    @admin.display(empty_value=None)
    def detection_name(self, obj):
        return obj.detection.name

    @admin.display(empty_value=None)
    def summary(self, obj):
        url = reverse('summary_image')
        return format_html(f"<a href='{url}?id={obj.detection.id}' target='_blank'>{obj.detection.summary_image()}</a>")

    @admin.display(empty_value='NA')
    def description(self, obj):
        # TODO: show survey component.
        if len(obj.conflict_source_detection_ids) == 1:
            sd = SourceDetection.objects.get(id=obj.conflict_source_detection_ids[0])
            return f"Single conflict with existing source '{sd.source.name}' from run '{sd.detection.run.name}'"

    @admin.display(empty_value=None)
    def compare(self, obj):
        if len(obj.conflict_source_detection_ids) == 1:
            url = reverse('summary_image')
            sd = SourceDetection.objects.get(id=obj.conflict_source_detection_ids[0])
            return format_html(f"<a href='{url}?id={sd.detection.id}' target='_blank'>{sd.detection.summary_image()}</a>")
        else:
            return None

    class AddToExistingSourceForm(forms.Form):
        title = 'Adding the following detections to existing sources'

    @action_form(AddToExistingSourceForm)
    def add_to_existing_source(self, request, queryset, form):
        """The case where there has been a released source in a different survey component.
        The new detection must be added to the existing source and the newly created source
        and source detection instances can be deleted.

        """
        try:
            for conflict in queryset:
                detection = conflict.detection
                sds = conflict.conflict_source_detection_ids
                if len(sds) != 1:
                    messages.error(request, f"Cannot add new detection {detection.name} to existing source if there are multiple potential sources.")
                sd_id = sds[0]

                # Delete current source and source detection
                sd_existing = SourceDetection.objects.get(detection=detection)
                logging.info(f"Deleting source {sd_existing.source.name} and corresponding source detection with id {sd_existing.id}")
                sd_existing.source.delete()
                sd_existing.delete()

                # Add to existing source
                source = Source.objects.get(id=sd_id)
                logging.info(f"Creating new source detection for detection {detection} and existing source {source}")
                SourceDetection.objects.create(
                    source=source,
                    detection=detection
                )
                logging.info("Conflict resolved")
                conflict.delete()
            return len(queryset)
        except Exception as e:
            messages.error(request, str(e))
            return
    add_to_existing_source.short_description = 'Add detection to existing source'

    def delete_new_source(self, request, queryset):
        """Case where there is an existing released source in the same survey component.
        New source and source detection instances can be deleted (detection effectively discarded).
        Does not matter if there are multiple source matches from other runs.

        """
        try:
            for conflict in queryset:
                sds = conflict.conflict_source_detection_ids
                sd_id = sds[0]

                # Delete current source and source detection
                sd_existing = SourceDetection.objects.get(detection=detection)
                logging.info(f"Deleting source {sd_existing.source.name} and corresponding source detection with id {sd_existing.id}")
                sd_existing.source.delete()
                sd_existing.delete()
                logging.info("Conflict resolved")
                conflict.delete()
            return len(queryset)
        except Exception as e:
            messages.error(request, str(e))
            return
    delete_new_source.short_description = 'Delete new source'

    class AddTagForm(forms.Form):
        title = 'Add tags'

    @add_tag_form(AddTagForm)
    def add_tag(self, request, queryset):
        try:
            # get or create tag
            tag_select = request.POST['tag_select']
            tag_create = str(request.POST['tag_create'])
            if tag_select == 'None':
                if tag_create == '':
                    messages.error(request, "No tag selected or created")
                    return
                else:
                    tag = Tag.objects.create(
                        name=tag_create
                    )
            else:
                tag = Tag.objects.get(id=int(tag_select))
            conflict_list = list(queryset)
            for c in conflict_list:
                d = c.detection
                source_detection = SourceDetection.objects.get(detection=d)
                TagSourceDetection.objects.create(
                    source_detection=source_detection,
                    tag=tag,
                    author=str(request.user)
                )
            return len(conflict_list)
        except Exception as e:
            messages.error(request, str(e))
            return
    add_tag.short_description = 'Add tags'

    class AddCommentForm(forms.Form):
        title = 'Add comments'

    @add_comment_form(AddCommentForm)
    def add_comment(self, request, queryset):
        try:
            detect_list = list(queryset)
            comment = str(request.POST['comment'])
            conflict_list = list(queryset)
            for c in conflict_list:
                d = c.detection
                Comment.objects.create(
                    comment=comment,
                    author=str(request.user),
                    detection=d
                )
            return len(conflict_list)
        except Exception as e:
            messages.error(request, str(e))
            return
    add_comment.short_description = 'Add comments'


admin.site.register(Run, RunAdmin)
admin.site.register(Instance, InstanceAdmin)
admin.site.register(Detection, DetectionAdmin)
admin.site.register(UnresolvedDetection, UnresolvedDetectionAdmin)
admin.site.register(ExternalConflict, ExternalConflictAdmin)
admin.site.register(SourceDetection, SourceDetectionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagSourceDetection, TagSourceDetectionAdmin)
admin.site.register(KinematicModel, KinematicModelAdmin)
