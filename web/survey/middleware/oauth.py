from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from social_django.models import UserSocialAuth
from keycloak import KeycloakOpenID


class KeycloakMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

        self.openid = KeycloakOpenID(server_url=settings.CLIENT_AUTH,
                                     client_id=settings.SOCIAL_AUTH_KEYCLOAK_KEY,
                                     realm_name=settings.REALM,
                                     client_secret_key=settings.SOCIAL_AUTH_KEYCLOAK_SECRET)

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            if user.is_staff is False:
                group = Group.objects.get(name='Basic')
                user.groups.add(group)
                user.is_staff = True
                user.save()

            auth = user.social_auth.first()
            if auth is None:
                response = self.get_response(request)
                return response
            data = self.openid.introspect(auth.extra_data.get('access_token'))
            if data.get('active', False) is False:
                logout(request)
                return redirect(settings.LOGIN_REDIRECT_URL)

        response = self.get_response(request)
        return response