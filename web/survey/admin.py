from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.forms import forms
from django.db import transaction
from random import choice

from survey.utils.base import ModelAdmin, ModelAdminInline
from survey.decorators import action_form
from survey.models import Detection, UnresolvedDetection,\
    Source, Instance, Run, SourceDetection, Comment, Tag, TagSourceDetection, KinematicModel


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
    list_per_page = 20
    list_display = ('id', 'run', 'name', 'x', 'y', 'z',
                    'f_sum', 'ell_maj', 'ell_min', 'w20', 'w50',
                    'detection_products_download')
    search_fields = ['run__name', 'name']

    def detection_products_download(self, obj):
        url = reverse('detection_products')
        return format_html(f"<a href='{url}?id={obj.id}'>Products</a>")

    detection_products_download.short_description = 'Products'

    def get_queryset(self, request):
        qs = super(DetectionAdmin, self).\
            get_queryset(request).\
            select_related('run')
        return qs.filter(unresolved=False)


class DetectionAdminInline(ModelAdminInline):
    model = Detection
    list_display = (
        'name', 'summary_image', 'x', 'y', 'z', 'f_sum',
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
    actions = ['check_action', 'resolve_action', 'manual_resolve']

    def get_actions(self, request):
        return super(UnresolvedDetectionAdmin, self).get_actions(request)

    def get_list_display(self, request):
        if request.GET:
            return 'id', 'summary_image', 'run', 'name', 'x', 'y', 'z', 'f_sum', 'ell_maj', 'ell_min',\
                   'w20', 'w50', 'moment0_image', 'spectrum_image'
        else:
            return 'id', 'summary_image', 'run', 'name', 'x', 'y', 'z', 'f_sum', 'ell_maj',\
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
                    print(detect_outer.id, detect_inner.id)
                    if detect_outer.is_match(detect_inner):
                        sanity, msg = detect_outer.sanity_check(detect_inner)
                        if sanity is False:
                            messages.info(request, msg)
                        else:
                            messages.info(request, "sanity passed")
                    else:
                        msg = f"Detections {detect_inner.id}, {detect_outer.id} are not in the same spacial and spectral range"  # noqa
                        messages.error(request, msg)
                        return
            return None
        except Exception as e:
            messages.error(request, str(e))
            return

    check_action.short_description = 'Sanity Check Detections'


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
        'run_manual_inspection'
    )
    inlines = (
        UnresolvedDetectionAdminInline,
        DetectionAdminInline,
        InstanceAdminInline,
    )

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


class RunAdminInline(ModelAdminInline):
    model = Run
    list_display = ['id', 'name', 'sanity_thresholds', 'run_products_download']
    fields = list_display
    readonly_fields = fields

    def run_products_download(self, obj):
        url = reverse('run_products')
        return format_html(f"<a href='{url}?id={obj.id}'>Products</a>")

    run_products_download.short_description = 'Products'


admin.site.register(Run, RunAdmin)
admin.site.register(Instance, InstanceAdmin)
admin.site.register(Detection, DetectionAdmin)
admin.site.register(UnresolvedDetection, UnresolvedDetectionAdmin)
admin.site.register(SourceDetection, SourceDetectionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagSourceDetection, TagSourceDetectionAdmin)
admin.site.register(KinematicModel, KinematicModelAdmin)
