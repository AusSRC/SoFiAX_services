import base64
import functools

from django.conf import settings
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from social_django.models import UserSocialAuth
from django.db import transaction

from keycloak import KeycloakOpenID


def action_form(form_class=None):
    """

    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, queryset):
            form = form_class()

            if 'confirm' in request.POST and request.POST:
                form = form_class(request.POST)
                if form.is_valid():
                    obj_count = func(self, request, queryset, form)
                    self.message_user(
                        request,
                        '%s objects updated' % obj_count
                    )
                    return None

            context = dict(
                self.admin_site.each_context(request),
                title=form_class.title,
                action=func.__name__,
                opts=self.model._meta,
                queryset=queryset, form=form,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME)

            return TemplateResponse(
                request,
                'admin/form_action_confirmation.html',
                context
            )

        wrapper.short_description = form_class.title

        return wrapper
    return decorator


def basic_auth(view):
    """Function requires user authentication.

    """
    def wrap(request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                return view(request, *args, **kwargs)

            if 'HTTP_AUTHORIZATION' in request.META:
                auth = request.META['HTTP_AUTHORIZATION'].split()
                if len(auth) == 2:
                    if auth[0].lower() == "basic":
                        username, password = base64.b64decode(auth[1]).decode("utf8").split(':')
                        openid = KeycloakOpenID(server_url=settings.CLIENT_AUTH,
                                                client_id=settings.SOCIAL_AUTH_KEYCLOAK_KEY,
                                                realm_name=settings.REALM,
                                                client_secret_key=settings.SOCIAL_AUTH_KEYCLOAK_SECRET)
                        token = openid.token(username, password)
                        userinfo = openid.userinfo(token['access_token'])
                        username = userinfo['preferred_username']
                        try:
                            user = User.objects.get(username=username)
                        except ObjectDoesNotExist:
                            with transaction.atomic():
                                user = User.objects.create_user(username, userinfo['email'])
                                group = Group.objects.get(name='Basic')
                                user.groups.add(group)
                                user.is_staff = True
                                user.save()

                                auth_user = UserSocialAuth.objects.create(user=user,
                                                                          provider='keycloak',
                                                                          uid=username,
                                                                          extra_data=token)
                                auth_user.save()

                        request.user = user
                        return view(request, *args, **kwargs)

            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic realm="AusSRC VO"'
            return response
        except Exception as e:
            response = HttpResponse(str(e))
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic realm="AusSRC VO"'
            return response
    return wrap
