"""Tags and comments (metadata module)."""

from django.contrib import admin
from modules.core.models import Comment, Tag
from modules.core.utils.base import EditableModelAdmin


class TagAdmin(EditableModelAdmin):
    list_display = ("name", "description", "type")
    fields = list_display


class CommentAdmin(EditableModelAdmin):
    list_display = ("comment", "detection", "updated_at")
    readonly_fields = ["author"]

    def save_model(self, request, obj, form, change):
        if obj.author is None:
            obj.author = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)
