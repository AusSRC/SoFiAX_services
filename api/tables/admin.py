from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.forms import forms
from django.db import transaction
from random import choice

from api.utils.base import ModelAdmin, ModelAdminInline
from api.decorators import action_form
from tables.models import Detection, UnresolvedDetection,\
    Instance, Run


class DetectionAdmin(ModelAdmin):
    model = Detection
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
        'name', 'x', 'y', 'z', 'f_sum',
        'ell_maj', 'ell_min', 'w20', 'w50', 'detection_products_download'
    )
    exclude = [
        'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max',
        'n_pix', 'f_min', 'f_max', 'rel', 'rms', 'ell_pa', 'ell3s_maj',
        'ell3s_min', 'ell3s_pa', 'kin_pa', 'err_x', 'err_y', 'err_z',
        'err_f_sum', 'ra', 'dec', 'freq', 'flag', 'unresolved', 'instance',
        'l', 'b', 'v_rad', 'v_opt', 'v_app'
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
        if request.GET:
            return super(UnresolvedDetectionAdmin, self).get_actions(request)
        return None

    def get_list_display(self, request):
        if request.GET:
            return 'id', 'name', 'x', 'y', 'z', 'f_sum', 'ell_maj', 'ell_min',\
                   'w20', 'w50', 'moment0_image', 'spectrum_image'
        else:
            return 'id', 'run', 'name', 'x', 'y', 'z', 'f_sum', 'ell_maj',\
                   'ell_min', 'w20', 'w50'

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
        detect_list = list(queryset)
        for index, detect_outer in enumerate(detect_list):
            for detect_inner in detect_list[index + 1:]:
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

    check_action.short_description = 'Sanity Check Detections'


class UnresolvedDetectionAdminInline(ModelAdminInline):
    model = UnresolvedDetection
    list_display = (
        'name', 'x', 'y', 'z', 'f_sum', 'ell_maj', 'ell_min', 'w20', 'w50'
    )
    exclude = [
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
        'id', 'name', 'sanity_thresholds', 'run_catalog',
        'run_link', 'run_products_download'
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
