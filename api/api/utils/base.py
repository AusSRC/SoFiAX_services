from django.contrib import admin


class ModelAdmin(admin.ModelAdmin):
    """Base class to implement shared methods in table Admin
    classes.

    """
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ModelAdminInline(admin.TabularInline):
    """Base class for table Admin inline classes.

    """
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
