from django.contrib import admin
from django.contrib.admin import helpers


class ModelAdmin(admin.ModelAdmin):
    """Base class to implement shared methods in table Admin
    classes.

    """
    show_change_link = True

    def changelist_view(self, request, extra_context=None):
        # Actions marked with acts_on_all = True run on the whole (filtered) changelist
        # when no rows are selected, instead of Django refusing with "Items must be selected".
        if request.method == 'POST' and 'action' in request.POST \
                and not request.POST.getlist(helpers.ACTION_CHECKBOX_NAME):
            action = self.get_actions(request).get(request.POST['action'])
            if action and getattr(action[0], 'acts_on_all', False):
                post = request.POST.copy()
                post['select_across'] = '1'
                # changelist_view only dispatches actions when something is selected; with
                # select_across the selected pks are ignored, so a placeholder is enough
                post.setlist(helpers.ACTION_CHECKBOX_NAME, ['0'])
                request.POST = post
        return super().changelist_view(request, extra_context)

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
