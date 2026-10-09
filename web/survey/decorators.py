import functools

from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from survey.models import Tag


# decorator for model action
def require_confirmation(func):
    def wrapper(modeladmin, request, queryset):
        if request.POST.get("confirmation") is None:
            request.current_app = modeladmin.admin_site.name
            context = {
                "action": request.POST["action"],
                "queryset": queryset,
            }
            return TemplateResponse(request, "admin/action_confirmation.html", context)

        return func(modeladmin, request, queryset)

    wrapper.__name__ = func.__name__
    return wrapper


def action_form(form_class=None):
    """ """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, queryset):
            form = form_class()

            if "confirm" in request.POST and request.POST:
                form = form_class(request.POST)
                if form.is_valid():
                    obj_count = func(self, request, queryset, form)
                    self.message_user(request, "%s objects updated" % obj_count)
                    return None

            context = dict(
                self.admin_site.each_context(request),
                title=form_class.title,
                action=func.__name__,
                opts=self.model._meta,
                queryset=queryset,
                form=form,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
            )

            return TemplateResponse(request, "admin/form_action_confirmation.html", context)

        wrapper.short_description = form_class.title

        return wrapper

    return decorator


def add_tag_form(form_class=None, tags=Tag.objects.all()):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, queryset):
            form = form_class()

            if "confirm" in request.POST and request.POST:
                form = form_class(request.POST)
                if form.is_valid():
                    func(self, request, queryset)
                return None

            context = dict(
                self.admin_site.each_context(request),
                title=form_class.title,
                action=func.__name__,
                opts=self.model._meta,
                queryset=queryset,
                tags=tags,
                form=form,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
            )

            return TemplateResponse(request, "admin/form_add_tag.html", context)

        wrapper.short_description = form_class.title

        return wrapper

    return decorator


def add_comment_form(form_class=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, queryset):
            form = form_class()

            if "confirm" in request.POST and request.POST:
                form = form_class(request.POST)
                if form.is_valid():
                    obj_count = func(self, request, queryset)
                    self.message_user(request, "%s objects updated" % obj_count)
                return None

            context = dict(
                self.admin_site.each_context(request),
                title=form_class.title,
                action=func.__name__,
                opts=self.model._meta,
                queryset=queryset,
                form=form,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
            )

            return TemplateResponse(request, "admin/form_add_comment.html", context)

        wrapper.short_description = form_class.title

        return wrapper

    return decorator
