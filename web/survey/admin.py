import math
import time
import logging
from random import choice

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.forms import forms
from django.db import transaction
from django.conf import settings
from django.shortcuts import redirect
from django.db.models.aggregates import Count
from django.db.models import Q

from survey.utils.base import ModelAdmin, ModelAdminInline
from survey.utils.task import task
from survey.utils.forms import _add_tag, _add_comment, _get_or_create_tag
from survey.utils.components import get_survey_components, get_release_name
from survey.decorators import action_form, add_tag_form, add_comment_form, require_confirmation
from survey.models import Detection, UnresolvedDetection, AcceptedDetection, ExternalConflict, \
    Instance, Run, Comment, Tag, TagDetection, Observation, SurveyComponent, \
    Task, ValueTaskReturn, SurveyComponentRun, Tile, SourceExtractionRegion

logging.basicConfig(level=logging.INFO)


def sanity_check(request, queryset):
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
                else:
                    # TODO(austin): could probably keep both of these sources if not match...
                    msg = f"Detections {detect_inner.id}, {detect_outer.id} are not in the same spacial and spectral range"  # noqa
                    messages.error(request, msg)
    except Exception as e:
        messages.error(request, str(e))


class TagAdmin(ModelAdmin):
    list_display = ('name', 'description', 'type')
    fields = list_display

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class CommentAdmin(ModelAdmin):
    list_display = ('comment', 'detection', 'updated_at')
    readonly_fields = ['author']

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


class ObservationAdmin(ModelAdmin):
    list_display = ['id', 'name', 'phase', 'sbid', 'quality', 'status', 'run_link', 'scheduled']
    search_fields = ['name', 'sbid', 'quality', 'status', 'scheduled']
    ordering = ('quality',)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(ObservationAdmin, self).get_queryset(request)
        return qs.filter(phase='Full Survey')

    def run_link(self, obj):
        if not obj.run:
            return '-'
        opts = self.model._meta
        url = reverse(f'admin:{opts.app_label}_run_changelist')
        return format_html(f"<a href='{url}?q={obj.run.name}'>{obj.run.name}</a>")

    run_link.short_description = 'Run'


class TileAdmin(ModelAdmin):
    list_display = ['id', 'name', 'ra_deg', 'dec_deg', 'phase', 'show_footprint', 'footprint_complete']
    search_fields = ['id', 'name', 'ra_deg', 'dec_deg', 'phase', 'tileobs__obs__name', 'tileobs__obs__sbid']

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(TileAdmin, self).get_queryset(request)
        qs = qs.annotate(footprint_complete=Count('tileobs',
                                                  filter=Q(tileobs__obs__status='COMPLETED'))).order_by('-footprint_complete')

        return qs.filter(phase='Survey')

    def show_footprint(self, obj):
        opts = self.model._meta
        url = reverse(f'admin:{opts.app_label}_observation_changelist')
        fmt = format_html_join(", ", "<a href='{}?q={}'>{}</a>", ((url, o.obs.name, o.obs.name) for o in obj.tileobs_set.all()))
        return fmt

    def footprint_complete(self, obj):
        total = obj.footprint_complete
        return total

    footprint_complete.admin_order_field = 'footprint_complete'
    footprint_complete.short_description = 'Footprints Complete'
    show_footprint.short_description = 'Footprints'


class SourceExtractionRegionAdmin(ModelAdmin):
    list_display = ['id', 'name', 'ra_deg', 'dec_deg', 'show_tiles', 'status', 'run_link', 'scheduled']
    search_fields = ['id', 'name', 'ra_deg', 'dec_deg', 'status', 'scheduled', 'sourceextractionregiontile__tile__name']

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def show_tiles(self, obj):
        opts = self.model._meta
        url = reverse(f'admin:{opts.app_label}_tile_changelist')
        fmt = format_html_join(", ", "<a href='{}?q={}'>{}</a>", ((url, t.tile.name, t.tile.name) for t in obj.sourceextractionregiontile_set.all()))
        return fmt

    show_tiles.short_description = 'Tiles'

    def run_link(self, obj):
        if not obj.run:
            return '-'
        opts = self.model._meta
        url = reverse(f'admin:{opts.app_label}_run_changelist')
        return format_html(f"<a href='{url}?q={obj.run.name}'>{obj.run.name}</a>")

    run_link.short_description = 'Run'


class SurveyComponentRunInline(admin.TabularInline):
    model = SurveyComponentRun
    extra = 1
    autocomplete_fields = ['run']

    def formfield_for_dbfield(self, *args, **kwargs):
        formfield = super().formfield_for_dbfield(*args, **kwargs)
        if formfield:
            formfield.widget.can_delete_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_add_related = False
            formfield.widget.can_view_related = True

        return formfield


class SurveyComponentAdmin(ModelAdmin):
    inlines = [SurveyComponentRunInline,]

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


class DetectionAdmin(ModelAdmin):
    model = Detection
    list_per_page = 50
    list_display = ('id', 'run', 'name', 'tags', 'comments', 'display_ra', 'display_dec', 'display_freq',
                    'display_f_sum', 'display_v_opt', 'display_rel', 'display_rms', 'display_snr',
                    'detection_products_download')
    search_fields = ['run__name', 'name']
    actions = ['mark_genuine', 'check_action', 'add_tag', 'add_comment']

    def display_ra(self, obj):
        return round(obj.ra, 4)
    display_ra.short_description = 'RA'

    def display_dec(self, obj):
        return round(obj.dec, 4)
    display_dec.short_description = 'Dec'

    def display_freq(self, obj):
        return round(obj.freq, 4)
    display_freq.short_description = 'freq'

    def display_f_sum(self, obj):
        return round(obj.f_sum, 4)
    display_f_sum.short_description = 'f sum'

    def display_v_opt(self, obj):
        return round(299792.458 * (1.42040575e+9 / obj.freq - 1.0), 4)
    display_v_opt.short_description = 'v_opt'

    def display_rel(self, obj):
        return round(obj.rel, 4)
    display_rel.short_description = 'rel'

    def display_rms(self, obj):
        return round(obj.rms, 4)
    display_rms.short_description = 'rms'

    def display_snr(self, obj):
        return round(obj.f_sum / obj.err_f_sum, 4)
    display_snr.short_description = 'snr'

    def check_action(self, request, queryset):
        sanity_check(request, queryset)

    check_action.short_description = 'Sanity Check Detections'

    @admin.display(empty_value=None)
    def tags(self, obj):
        return ', '.join(td.tag.name for td in TagDetection.objects.filter(detection=obj))

    @admin.display(empty_value=None)
    def comments(self, obj):
        return ', '.join(c.comment for c in Comment.objects.filter(detection=obj))

    @admin.display(empty_value=None)
    def summary(self, obj):
        url = reverse('summary_image')
        return format_html(f"<a href='{url}?id={obj.id}' target='_blank'>{obj.summary_image()}</a>")

    def get_actions(self, request):
        return super(DetectionAdmin, self).get_actions(request)

    def get_list_display(self, request):
        return 'id', 'run', 'tags', 'comments', 'summary', 'name', 'display_ra', 'display_dec', 'display_freq', \
               'display_f_sum', 'display_v_opt', 'display_rel', 'display_rms', 'display_snr'

    def detection_products_download(self, obj):
        url = reverse('detection_products')
        return format_html(f"<a href='{url}?id={obj.id}'>Products</a>")

    detection_products_download.short_description = 'Products'

    def get_queryset(self, request):
        qs = super(DetectionAdmin, self).\
            get_queryset(request).\
            select_related('run')
        return qs.filter(unresolved=False)

    class AcceptDetectionAction(forms.Form):
        title = 'These detections will be marked as real sources.'

    def accept_detection(self, request, queryset):
        try:
            with transaction.atomic():
                detect_list = list(queryset.select_for_update())
                run_set = {detect.run.id for detect in detect_list}
                if len(run_set) > 1:
                    messages.error(
                        request,
                        "Detections from multiple runs selected")
                    return 0

                # Create source and source detection entries
                for d in detect_list:
                    d.accepted = True
                messages.info(request, f"Accepted {len(detect_list)} detections.")
                return
        except Exception as e:
            messages.error(request, str(e))
            return
    accept_detection.short_description = 'Accept Detections'

    class AddTagForm(forms.Form):
        title = 'Add tags'

    @add_tag_form(AddTagForm)
    def add_tag(self, request, queryset):
        with transaction.atomic():
            for d in queryset:
                _add_tag(request, d)
        return len(queryset)
    add_tag.short_description = 'Add tags'

    class AddCommentForm(forms.Form):
        title = 'Add comments'

    @add_comment_form(AddCommentForm)
    def add_comment(self, request, queryset):
        with transaction.atomic():
            for d in queryset:
                _add_comment(request, d)
        return len(queryset)
    add_comment.short_description = 'Add comments'

    def lookup_allowed(self, lookup, value):
        return True


class DetectionAdminInline(ModelAdminInline):
    # TODO(austin): probably want to show tags if there are any?
    model = Detection
    readonly_fields = (
        'name', 'display_x', 'display_y', 'display_z', 'display_f_sum',
        'display_ell_maj', 'display_ell_min', 'display_w20', 'display_w50', 'detection_products_download'
    )
    exclude = ['x', 'y', 'z', 'f_sum', 'ell_min', 'ell_maj', 'w20', 'w50', 'wm50',
        'x_peak', 'y_peak', 'z_peak', 'ra_peak', 'dec_peak', 'freq_peak',
        'b_peak', 'l_peak', 'v_rad_peak', 'v_opt_peak', 'v_app_peak',
        'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max', 'n_pix', 'f_min',
        'f_max', 'rel', 'rms', 'ell_pa', 'ell3s_maj', 'ell3s_min', 'ell3s_pa',
        'kin_pa', 'err_x', 'err_y', 'err_z', 'err_f_sum', 'ra', 'dec', 'freq',
        'flag', 'unresolved', 'instance', 'l', 'b', 'v_rad', 'v_opt', 'v_app'
    ]
    #readonly_fields = list_display
    fk_name = 'run'

    def display_tags(self, obj):
        return ', '.join([td.name for td in TagDetection.objects.get(detection=obj)])

    def display_comments(self, obj):
        return ', '.join([c.comment for c in Comment.objects.get(detection=obj)])

    def display_x(self, obj):
        return round(obj.x, 4)
    display_x.short_description = 'x'

    def display_y(self, obj):
        return round(obj.y, 4)
    display_y.short_description = 'y'

    def display_z(self, obj):
        return round(obj.z, 4)
    display_z.short_description = 'z'

    def display_f_sum(self, obj):
        return round(obj.f_sum, 4)
    display_f_sum.short_description = 'f sum'

    def display_ell_maj(self, obj):
        return round(obj.ell_maj, 4)
    display_ell_maj.short_description = 'ell maj'

    def display_ell_min(self, obj):
        return round(obj.ell_min, 4)
    display_ell_min.short_description = 'ell min'

    def display_w20(self, obj):
        return round(obj.w20, 4)
    display_w20.short_description = 'w20'

    def display_w50(self, obj):
        return round(obj.w50, 4)
    display_w50.short_description = 'w50'

    def detection_products_download(self, obj):
        url = reverse('detection_products')
        return format_html(f"<a href='{url}?id={obj.id}'>Products</a>")

    detection_products_download.short_description = 'Products'

    def get_queryset(self, request):
        qs = super(DetectionAdminInline, self).get_queryset(request)
        return qs.filter(unresolved=False, n_pix__gte=300, rel__gte=0.7)


class UnresolvedDetectionAdmin(ModelAdmin):
    model = UnresolvedDetection
    actions = ['check_action', 'resolve_action', 'manual_resolve', 'add_tag', 'add_comment']

    def display_x(self, obj):
        return round(obj.x, 4)
    display_x.short_description = 'x'

    def display_y(self, obj):
        return round(obj.y, 4)
    display_y.short_description = 'y'

    def display_z(self, obj):
        return round(obj.z, 4)
    display_z.short_description = 'z'

    def display_f_sum(self, obj):
        return round(obj.f_sum, 4)
    display_f_sum.short_description = 'f sum'

    def display_ell_maj(self, obj):
        return round(obj.ell_maj, 4)
    display_ell_maj.short_description = 'ell maj'

    def display_ell_min(self, obj):
        return round(obj.ell_min, 4)
    display_ell_min.short_description = 'ell min'

    def display_w20(self, obj):
        return round(obj.w20, 4)
    display_w20.short_description = 'w20'

    def display_w50(self, obj):
        return round(obj.w50, 4)
    display_w50.short_description = 'w50'

    @admin.display(empty_value='None')
    def source(self, obj):
        return obj.source_name

    @admin.display(empty_value=None)
    def tags(self, obj):
        tds = TagDetection.objects.filter(detection=obj)
        if len(tds) > 0:
            tag_string = ', '.join([td.tag.name for td in tds])
            return tag_string

    @admin.display(empty_value=None)
    def summary(self, obj):
        url = reverse('summary_image')
        return format_html(f"<a href='{url}?id={obj.id}' target='_blank'>{obj.summary_image()}</a>")

    def get_actions(self, request):
        return super(UnresolvedDetectionAdmin, self).get_actions(request)

    def get_list_display(self, request):
        if request.GET:
            return 'id', 'source', 'tags', 'summary', 'run', 'name', 'display_x', 'display_y', 'display_z', 'display_f_sum', 'display_ell_maj', 'display_ell_min',\
                   'display_w20', 'display_w50', 'moment0_image', 'spectrum_image'
        else:
            return 'id', 'run', 'name', 'display_x', 'display_y', 'display_z', 'display_f_sum', 'display_ell_maj',\
                   'display_ell_min', 'display_w20', 'display_w50', 'moment0_image', 'spectrum_image'

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
        sanity_check(request, queryset)

    check_action.short_description = 'Sanity Check Detections'

    class AddTagForm(forms.Form):
        title = 'Add tags'

    @add_tag_form(AddTagForm)
    def add_tag(self, request, queryset):
        with transaction.atomic():
            for d in queryset:
                _add_tag(request, d)
        return len(queryset)
    add_tag.short_description = 'Add tags'

    class AddCommentForm(forms.Form):
        title = 'Add comments'

    @add_comment_form(AddCommentForm)
    def add_comment(self, request, queryset):
        with transaction.atomic():
            for d in queryset:
                _add_comment(request, d)
        return len(queryset)
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


class AcceptedDetectionAdmin(ModelAdmin):
    # TODO(austin): probably want to show tags if there are any?
    model = Detection
    readonly_fields = (
        'name', 'display_x', 'display_y', 'display_z', 'display_f_sum',
        'display_ell_maj', 'display_ell_min', 'display_w20', 'display_w50', 'detection_products_download'
    )
    exclude = [
        'x', 'y', 'z', 'f_sum', 'ell_min', 'ell_maj', 'w20', 'w50', 'wm50',
        'x_peak', 'y_peak', 'z_peak', 'ra_peak', 'dec_peak', 'freq_peak',
        'b_peak', 'l_peak', 'v_rad_peak', 'v_opt_peak', 'v_app_peak',
        'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max', 'n_pix', 'f_min',
        'f_max', 'rel', 'rms', 'ell_pa', 'ell3s_maj', 'ell3s_min', 'ell3s_pa',
        'kin_pa', 'err_x', 'err_y', 'err_z', 'err_f_sum', 'ra', 'dec', 'freq',
        'flag', 'unresolved', 'instance', 'l', 'b', 'v_rad', 'v_opt', 'v_app'
    ]
    actions = ['deselect']
    fk_name = 'run'

    def display_x(self, obj):
        return round(obj.x, 4)
    display_x.short_description = 'x'

    def display_y(self, obj):
        return round(obj.y, 4)
    display_y.short_description = 'y'

    def display_z(self, obj):
        return round(obj.z, 4)
    display_z.short_description = 'z'

    def display_f_sum(self, obj):
        return round(obj.f_sum, 4)
    display_f_sum.short_description = 'f sum'

    def display_ell_maj(self, obj):
        return round(obj.ell_maj, 4)
    display_ell_maj.short_description = 'ell maj'

    def display_ell_min(self, obj):
        return round(obj.ell_min, 4)
    display_ell_min.short_description = 'ell min'

    def display_w20(self, obj):
        return round(obj.w20, 4)
    display_w20.short_description = 'w20'

    def display_w50(self, obj):
        return round(obj.w50, 4)
    display_w50.short_description = 'w50'

    def detection_products_download(self, obj):
        url = reverse('detection_products')
        return format_html(f"<a href='{url}?id={obj.id}'>Products</a>")

    detection_products_download.short_description = 'Products'

    def deselect(self, request, queryset):
        with transaction.atomic():
            for d in queryset:
                d.accepted = False
                d.save()
        return len(queryset)
    deselect.short_description = 'Deselect detection'

    @admin.display(empty_value=None)
    def summary(self, obj):
        url = reverse('summary_image')
        return format_html(f"<a href='{url}?id={obj.id}' target='_blank'>{obj.summary_image()}</a>")

    def get_queryset(self, request):
        qs = super(AcceptedDetectionAdmin, self).get_queryset(request).select_related('run')
        return qs.filter(accepted=True, n_pix__gte=300, rel__gte=0.7)

    def get_list_display(self, request):
        if request.GET:
            return 'id', 'summary', 'run', 'name', 'display_x', 'display_y', 'display_z', 'display_f_sum', 'display_ell_maj', 'display_ell_min',\
                   'display_w20', 'display_w50', 'moment0_image', 'spectrum_image'
        else:
            return 'id', 'run', 'name', 'display_x', 'display_y', 'display_z', 'display_f_sum', 'display_ell_maj',\
                   'display_ell_min', 'display_w20', 'display_w50', 'moment0_image', 'spectrum_image'


class AcceptedDetectionAdminInline(ModelAdminInline):
    model = AcceptedDetection
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
        qs = super(AcceptedDetectionAdminInline, self).get_queryset(request)
        return qs.filter(accepted=True)


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
        'id', 'name', 'created', 'sanity_thresholds',
        'run_unresolved_detections', 'run_accepted_detections', 'run_detections',
        'run_manual_inspection', 'run_external_conflicts',)
    inlines = (
        UnresolvedDetectionAdminInline,
        AcceptedDetectionAdminInline,
        DetectionAdminInline,
        InstanceAdminInline
    )
    ordering = ('-created',)
    search_fields = ['name']
    actions = ['_internal_cross_match', '_external_cross_match',
               '_release_sources', '_delete_run']

    def has_delete_permission(self, request, obj=None):
        return False

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

    def run_unresolved_detections(self, obj):
        opts = self.model._meta
        url = reverse(f'admin:{opts.app_label}_unresolveddetection_changelist')
        return format_html(f"<a href='{url}?run={obj.id}'>Unresolved Detections</a>")
    run_unresolved_detections.short_description = 'Unresolved Detections'

    def run_accepted_detections(self, obj):
        opts = self.model._meta
        url = reverse(f'admin:{opts.app_label}_accepteddetection_changelist')
        return format_html(f"<a href='{url}?run={obj.id}'>Accepted Detections</a>")
    run_accepted_detections.short_description = 'Accepted Detections'

    def run_detections(self, obj):
        opts = self.model._meta
        url = reverse(f'admin:{opts.app_label}_detection_changelist')
        return format_html(f"<a href='{url}?run={obj.id}'>All Detections</a>")
    run_detections.short_description = 'All Detections'

    def run_manual_inspection(self, obj):
        url = f"{reverse('inspect_detection')}?run_id={obj.id}"
        return format_html(f"<a href='{url}'>Manual inspection</a>")
    run_manual_inspection.short_description = 'Manual inspection'

    def run_external_conflicts(self, obj):
        url = f"{reverse('external_conflict')}?run_id={obj.id}"
        return format_html(f"<a href='{url}'>External conflicts</a>")
    run_external_conflicts.short_description = 'External conflicts'

    def _is_match(self, d1, d2, thresh_spat=90.0, thresh_spec=2e+6):
        """Check if two detections are a match based on spatial and spectral separation.

        """
        try:
            ra_i = d1.ra * math.pi / 180.0
            dec_i = d1.dec * math.pi / 180.0
            ra_j = d2.ra * math.pi / 180.0
            dec_j = d2.dec * math.pi / 180.0
            r_spat = 3600.0 * (180.0 / math.pi) * math.acos(math.sin(dec_i) * math.sin(dec_j) + math.cos(dec_i) * math.cos(dec_j) * math.cos(ra_i - ra_j))
            r_spec = abs(d1.freq - d2.freq)
        except Exception as e:
            raise Exception(f"Math error {e}")
        if r_spat < thresh_spat and r_spec < thresh_spec:
            return True
        return False

    @task(exclusive_func_with=['internal_cross_match', 'external_cross_match', 'release_sources', 'delete_run'])
    def delete_run(self, request, queryset):
        names = [i.name for i in queryset]
        with transaction.atomic():
            queryset._raw_delete(queryset.db)
        return ValueTaskReturn(f'Run(s) deleted: {names}')

    @require_confirmation
    def _delete_run(self, request, queryset):
        try:
            if queryset.count() == 0:
                messages.error(request, "No Run(s) selected")
                return

            self.delete_run(request, queryset)
            return redirect('/admin/survey/task/')
        except Exception as e:
            messages.error(request, str(e))

    _delete_run.short_description = 'Delete Run'

    def _internal_cross_match(self, request, queryset):
        try:
            task_id = self.internal_cross_match(request, queryset)
            logging.info(f'Created task {task_id} for internal cross matching')
            return redirect('/admin/survey/task/')
        except Exception as e:
            messages.error(request, str(e))

    @task(exclusive_func_with=['internal_cross_match', 'external_cross_match', 'release_sources', 'delete_run'])
    def internal_cross_match(self, request, queryset):
        """Run the internal cross matching workflow

        """
        if queryset.count() != 1:
            raise Exception("Only one run can be selected at a time for internal cross matching.")

        run = queryset.first()

        with transaction.atomic():
            # This filter is here to lock all the detections
            Detection.objects.filter(run=run).select_for_update()
            all_run_detections = Detection.objects.filter(
                run=run,
                unresolved=False,
                n_pix__gte=300,
                rel__gte=0.7
            )

            if any([d.unresolved for d in all_run_detections]):
                raise Exception('There cannot be any unresolved detections for the run at the time of running internal cross matching.')

            detections = list(Detection.objects.filter(run=run, accepted=True))

            # cross match internally
            logging.info('The following pairs of detections have been marked as unresolved:')
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
                        logging.info(f'{d1.name}, {d2.name}')

            return ValueTaskReturn(f'Completed internal cross matching for {run.name}')

    _internal_cross_match.short_description = 'Internal cross matching'

    @task(exclusive_func_with=['internal_cross_match', 'external_cross_match', 'release_sources', 'delete_run'])
    def external_cross_match(self, request, queryset):
        # Threshold values
        thresh_spat = 90.0
        thresh_spec = 2e+6
        thresh_spat_auto = 5.0
        thresh_spec_auto = 0.05e+6
        SEARCH_THRESHOLD = 1.0

        if queryset.count() != 1:
            raise Exception("Only one run can be selected at a time for external cross matching.")

        # Check to make sure run is in survey_components
        run = queryset.first()
        survey_component_runs = []
        survey_components = get_survey_components()
        for runs in survey_components.values():
            survey_component_runs += runs

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
            run_detections = Detection.objects.filter(run=run, accepted=True)  # Accepted detections that are not yet sources

            if any([d.unresolved for d in run_detections]):
                raise Exception('There cannot be any unresolved detections for the run at the time of running external cross matching.')

            # Detections from run must enter into one of these lists
            accepted_detections = []
            all_rename_detections = []
            external_conflicts = []

            logging.info(f'External cross matching applied in {run.name} to {len(run_detections)} detections')
            start = time.time()
            for idx, d in enumerate(run_detections):
                auto_rename = False
                auto_delete = False
                matches = []
                delete_detections = []
                rename_detections = []

                # Compare against close detections (accepted) from other runs.
                # TODO: Fix this threshold for the poles with delta RA (cosine factor)
                close_detections = Detection.objects.filter(
                    accepted=True,
                    source_name__isnull=False,
                    ra__range=(d.ra - SEARCH_THRESHOLD, d.ra + SEARCH_THRESHOLD),
                    dec__range=(d.dec - SEARCH_THRESHOLD, d.dec + SEARCH_THRESHOLD),
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
                    logging.info(f'[{idx+1}/{len(run_detections)}] {d.name} to be automatically deleted. Conflict: {delete_detections}')

                if auto_rename and not auto_delete:
                    if len(rename_detections) > 1:
                        logging.error(f'Multiple rename sources: {rename_detections}')
                        raise Exception('Should not be able to rename a detection to more than one source (existing database conflict to resolve).')

                    # Check other detections pointing to rename source in same survey component
                    conflict_in_survey_component = False
                    d_cur, d_ext = rename_detections[0]
                    ds = Detection.objects.filter(source_name=d_ext.source_name)
                    for d in ds:
                        if set([d_cur.run.name, d.run.name]).issubset(set(runs)):
                            conflict_in_survey_component = True
                            logging.info(f'Cannot rename detection {d_cur.name} to {d_ext.source_name} due to potential conflict {d.name} in same survey component.')
                            logging.info(f'Creating external conflict {d_cur.name} to detection {d.name}')
                            external_conflicts.append({
                                'run': run,
                                'detection': d_cur,
                                'conflict_detection': d_ext
                            })
                    if not conflict_in_survey_component:
                        all_rename_detections += rename_detections
                        logging.info(f'[{idx+1}/{len(run_detections)}] {d.name} to be automatically renamed to {d_ext.source_name} [{d_ext.run.name}]')

                if not auto_rename and not auto_delete and matches:
                    logging.info(f'[{idx+1}/{len(run_detections)}] Matches found for {d.name}: {matches} to resolve manually')
                    for d_ext_match in matches:
                        external_conflicts.append({
                            'run': run,
                            'detection': d,
                            'conflict_detection': d_ext_match
                        })
                if not auto_rename and not auto_delete and not matches:
                    accepted_detections.append(d)
                    logging.info(f'[{idx+1}/{len(run_detections)}] {d.name} will be accepted')

            end = time.time()
            logging.info(f"External cross matching completed in {round(end - start, 2)} seconds")

            # Release name check
            accepted_source_names = set([get_release_name(d.name) for d in accepted_detections])
            existing_names = set([d.source_name for d in Detection.objects.filter(accepted=True, source_name__isnull=False)])
            if accepted_source_names & existing_names:
                logging.error('External cross matching failed - release name already exists for accepted detection.')
                raise Exception(f'Attempting to rename to: {accepted_source_names.intersection(existing_names)}')

            logging.info("Writing updates to database")
            # Accepted sources
            for d in accepted_detections:
                release_name = get_release_name(d.name)
                d.name = release_name
                d.save()

            # Renaming
            logging.info(f'Renaming: {all_rename_detections}')
            for (d, new_d) in all_rename_detections:
                # Check if deleted in this run
                logging.info(f'Database update: Renaming {d.source_name} to {new_d.source_name}')
                d.source_name = new_d.source_name
                d.save()

            # External conflicts
            for ex_c in external_conflicts:
                ExternalConflict.objects.get_or_create(**ex_c)

            logging.info("Updating database complete")
            return ValueTaskReturn(f'Completed {run.name} external cross matching')

    def _external_cross_match(self, request, queryset):
        """Run the external cross matching workflow to identify sources
        that conflict with sources from other survey components.

        """
        try:
            task_id = self.external_cross_match(request, queryset)
            logging.info(f'Created task {task_id} for external cross matching')
            return redirect('/admin/survey/task/')
        except Exception as e:
            messages.error(request, str(e))

    _external_cross_match.short_description = 'External cross matching'

    class ReleaseSourceForm(forms.Form):
        title = 'Release sources for selected runs. Created source names and adds new tag to all sources.'

    @task(exclusive_func_with=['internal_cross_match', 'external_cross_match', 'release_sources', 'delete_run'])
    def release_sources(self, request, queryset, tag):
        PROJECT = settings.PROJECT

        with transaction.atomic():
            for run in queryset:
                logging.info(f"Preparing release for run {run.name}")

                detections = Detection.objects.filter(run=run, accepted=True).filter(run=run, source_name__isnull=False).select_for_update()
                release_detections = detections.filter(accepted=True, source_name__isnull=False)
                reject_detections = detections.filter(accepted=True, source_name__isnull=True)  # NOTE: there shouldn't be any of these

                if len(ExternalConflict.objects.filter(run_id=run.id)) != 0:
                    raise Exception('There cannot be any external conflicts when creating release source names.')
                if any([d.unresolved for d in release_detections]):
                    raise Exception('There cannot be any unresolved detections when releasing sources.')

                logging.info(f"{len(release_detections)} detections to release, {len(reject_detections)} detections to reject.")

                # Release sources
                for idx, d in enumerate(release_detections):
                    existing = TagDetection.objects.filter(tag=tag, detection=d)
                    if not existing:
                        logging.info(f'[{idx+1}/{len(release_detections)}] Creating TagDetection entry for Source {d.source_name}')
                        TagDetection.objects.create(
                            tag=tag,
                            detection=d,
                            author=str(request.user))
                    else:
                        logging.info(f'Tag already created for Source {d.source_name}')

                # Delete sources
                logging.info('Deleting remaining source detections and source objects (with SoFiA name).')
                for idx, d in enumerate(reject_detections):
                    logging.info(f'[{idx+1}/{len(reject_detections)}] Rejecting detection {d.name}')
                    d.accepted = False
                    d.save()

                logging.info("Release completed")

            names = [run.name for run in queryset]
            return ValueTaskReturn(f'Completed release for {",".join(names)}')

    @add_tag_form(ReleaseSourceForm)
    def _release_sources(self, request, queryset):
        """Create releases for a given run. This will update source names to be
        official release names and create a new tag for all sources.

        Needs for there to be no internal or external conflicts.

        """
        try:
            tag = _get_or_create_tag(request)
            task_id = self.release_sources(request, queryset, tag)
            logging.info(f'Created task {task_id} for releasing sources')
            # TODO: update metadata in data products here...
            # TODO: calculate derived properties (hi_cor, f_sum_cor)

            return redirect('/admin/survey/task/')
        except Exception as e:
            messages.error(request, str(e))
            return

    _release_sources.short_description = 'Release sources'


class TaskAdmin(ModelAdmin):
    list_display = ['id', 'func', 'queryset', 'start', 'end', 'state', 'error', 'get_retval', 'get_return_link']

    def delete_queryset(self, request, queryset):
        for i in queryset:
            if i.state == 'RUNNING':
                messages.error(request, f"{i.id} is RUNNING")
                return
        with transaction.atomic():
            queryset.delete()

    def get_queryset(self, request):
        return super().get_queryset(request).filter(user__contains=str(request.user))

    def get_retval(self, obj):
        ret = obj.get_return()
        if ret:
            return str(ret)
        return None

    def get_return_link(self, obj):
        return obj.get_return_link()

    def has_delete_permission(self, request, obj=None):
        return True

    get_retval.short_description = 'Return'
    get_return_link.short_description = 'Link'


admin.site.register(Run, RunAdmin)
admin.site.register(Instance, InstanceAdmin)
admin.site.register(Detection, DetectionAdmin)
admin.site.register(UnresolvedDetection, UnresolvedDetectionAdmin)
admin.site.register(AcceptedDetection, AcceptedDetectionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)

#if settings.KINEMATICS:
#    admin.site.register(KinematicModel, KinematicModelAdmin)

admin.site.register(SourceExtractionRegion, SourceExtractionRegionAdmin)
admin.site.register(SurveyComponent, SurveyComponentAdmin)
admin.site.register(Observation, ObservationAdmin)
admin.site.register(Tile, TileAdmin)
admin.site.register(Task, TaskAdmin)
