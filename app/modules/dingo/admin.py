"""Admin pages of the DINGO module: GAMA matches of the accepted and rejected detections."""

from django.contrib import admin
from django.utils.html import format_html_join, mark_safe

from modules.core.admin.detections import AcceptedDetectionAdmin as CoreAcceptedDetectionAdmin
from modules.core.admin.detections import RejectedDetectionAdmin as CoreRejectedDetectionAdmin
from modules.core.models import AcceptedDetection, RejectedDetection


class GAMAColumn:
    """Column with the GAMA catalogue objects near a detection, shown after the comments."""

    @admin.display(empty_value=None)
    def GAMA_matches(self, obj):
        return format_html_join(mark_safe("<br>"), "{}", ((g.cata_id,) for g in obj.detectionnearestgama_set.all()))

    def get_list_display(self, request):
        columns = super().get_list_display(request)
        if "comments" not in columns:
            return columns
        index = columns.index("comments") + 1
        return (*columns[:index], "GAMA_matches", *columns[index:])


class AcceptedDetectionAdmin(GAMAColumn, CoreAcceptedDetectionAdmin):
    pass


class RejectedDetectionAdmin(GAMAColumn, CoreRejectedDetectionAdmin):
    pass


# The detection pages of the core module with the additions of this module
admin.site.unregister(AcceptedDetection)
admin.site.register(AcceptedDetection, AcceptedDetectionAdmin)
admin.site.unregister(RejectedDetection)
admin.site.register(RejectedDetection, RejectedDetectionAdmin)
