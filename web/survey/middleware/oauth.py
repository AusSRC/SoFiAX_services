import json

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from keycloak import KeycloakOpenID
from django.http import HttpResponse


class KeycloakMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.groups = settings.AUTH_GROUPS
        self.openid = KeycloakOpenID(
            server_url=settings.CLIENT_AUTH,
            client_id=settings.SOCIAL_AUTH_KEYCLOAK_KEY,
            realm_name=settings.REALM,
            client_secret_key=settings.SOCIAL_AUTH_KEYCLOAK_SECRET
        )

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

            extra = auth.extra_data
            if isinstance(extra, str):
                extra = json.loads(extra)
            # validate access token
            data = self.openid.introspect(extra.get('access_token'))
            # check user is a member of group that can access site
            jwt_groups = data.get('user_groups', None)
            if jwt_groups:
                if any(item in self.groups for item in jwt_groups) is False:
                    err = f"Unauthorized, not a member of any group: {', '.join(self.groups)}"
                    return HttpResponse(err, status=401)

            if data.get('active', False) is False:
                logout(request)
                return redirect(settings.LOGIN_REDIRECT_URL)

        response = self.get_response(request)
        return response
