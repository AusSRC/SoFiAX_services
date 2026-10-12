"""Background tasks (core module)."""

from django.contrib import admin, messages
from django.db import transaction
from modules.core.models import Task
from modules.core.utils.base import ModelAdmin


class TaskAdmin(ModelAdmin):
    list_display = ["id", "func", "view_queryset", "start", "end", "state", "error", "get_retval", "get_return_link"]

    def delete_queryset(self, request, queryset):
        for i in queryset:
            if i.state == "RUNNING":
                messages.error(request, f"{i.id} is RUNNING")
                return
        with transaction.atomic():
            queryset.delete()

    def get_queryset(self, request):
        return super().get_queryset(request).filter(user__contains=str(request.user))

    def view_queryset(self, obj):
        qs = obj.queryset
        if not qs:
            return ""

        if len(qs) > 5:
            return f"{qs[0]} , ... , {qs[-1]}"

        return ",".join(qs)

    view_queryset.short_description = "Query Set"

    def get_retval(self, obj):
        ret = obj.get_return()
        if ret:
            return str(ret)
        return None

    def get_return_link(self, obj):
        return obj.get_return_link()

    def has_delete_permission(self, request, obj=None):
        return True

    get_retval.short_description = "Return"
    get_return_link.short_description = "Link"


admin.site.register(Task, TaskAdmin)
