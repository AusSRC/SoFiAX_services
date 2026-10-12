import functools
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from modules.core.models import Tag


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


def _form_action(form_class, template, pass_form=False, report=True, context=None):
    """Admin action that shows a form before it is run on the selected objects.

    pass_form: the action takes the form as an argument
    report: show how many objects were updated from the return value of the action
    context: function that returns additional context for the template
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, queryset):
            form = form_class()

            if "confirm" in request.POST and request.POST:
                form = form_class(request.POST)
                if form.is_valid():
                    args = (form,) if pass_form else ()
                    obj_count = func(self, request, queryset, *args)
                    if report:
                        self.message_user(request, "%s objects updated" % obj_count)
                    return None

            template_context = dict(
                self.admin_site.each_context(request),
                title=form_class.title,
                action=func.__name__,
                opts=self.model._meta,
                queryset=queryset,
                form=form,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
            )
            if context:
                template_context.update(context())

            return TemplateResponse(request, template, template_context)

        wrapper.short_description = form_class.title

        return wrapper

    return decorator


def action_form(form_class=None):
    return _form_action(form_class, "admin/form_action_confirmation.html", pass_form=True)


def add_tag_form(form_class=None):
    return _form_action(
        form_class, "admin/form_add_tag.html", report=False, context=lambda: {"tags": Tag.objects.all()}
    )


def add_comment_form(form_class=None):
    return _form_action(form_class, "admin/form_add_comment.html")
