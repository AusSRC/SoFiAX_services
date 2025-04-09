import os
import environ
from pathlib import Path

# Initialise environment variables
env = environ.Env(
    KINEMATICS=(bool, True)
)
environ.Env.read_env()

# ---------------------------------------------------------------------------------------
# Deployment settings

PROJECT = env('PROJECT')
if not PROJECT:
    raise Exception("Project not defined")

AUTH_GROUPS = env('AUTH_GROUPS').split(' ')
PROJECT = PROJECT.upper()
LOCAL = bool(env('LOCAL', default=True))
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env('DEBUG')
USE_X_FORWARDED_HOST = True
CSRF_TRUSTED_ORIGINS=['https://*.aussrc.org']

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS').split(' ')
SITE_NAME = env("SITE_NAME")
SITE_HEADER = env("SITE_HEADER")
SITE_TITLE = env("SITE_TITLE")
INDEX_TITLE = env("INDEX_TITLE")

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

KINEMATICS = env('KINEMATICS')

# ---------------------------------------------------------------------------------------
# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'sslserver',
    'django_extensions',
    'social_django',
    'survey',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if LOCAL is False:
    MIDDLEWARE.append('social_django.middleware.SocialAuthExceptionMiddleware',)
    MIDDLEWARE.append('survey.middleware.oauth.KeycloakMiddleware',)

AUTHENTICATION_BACKENDS = []

if LOCAL is False:
    AUTHENTICATION_BACKENDS.append('social_core.backends.keycloak.KeycloakOAuth2',)

AUTHENTICATION_BACKENDS.append('django.contrib.auth.backends.ModelBackend')

## Social Auth
LOGIN_URL = '/oauth/login/keycloak'
LOGIN_REDIRECT_URL = '/admin'
LOGOUT_URL = env('LOGOUT_URL', default='/logout')

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_JSONFIELD_CUSTOM = 'django.db.models.JSONField'
SOCIAL_AUTH_SESSION_EXPIRATION = True
SOCIAL_AUTH_FORCE_POST_DISCONNECT = True
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

SITE_ID = 1

if LOCAL is False:
    SOCIAL_AUTH_KEYCLOAK_KEY = env('KEY')
    SOCIAL_AUTH_KEYCLOAK_SECRET = env('SECRET')
    REALM = env('REALM')
    SOCIAL_AUTH_KEYCLOAK_PUBLIC_KEY = env('PUBLIC_KEY')
    CLIENT_AUTH = env('CLIENT_AUTH')
    SOCIAL_AUTH_KEYCLOAK_AUTHORIZATION_URL=env('AUTHORIZATION_URL')
    SOCIAL_AUTH_KEYCLOAK_ACCESS_TOKEN_URL=env('ACCESS_TOKEN_URL')
    ID_KEY = env('ID_KEY')
## End Social Auth

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'survey/templates/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------------------------------------
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASE_HOST = env('DATABASE_HOST')
DATABASE_PORT = env('DATABASE_PORT')
DATABASE_NAME = env('DATABASE_NAME')
DATABASE_USER = env('DATABASE_USER')
DATABASE_PASSWORD = env('DATABASE_PASSWORD')
SEARCH_PATH = env('SEARCH_PATH')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': f'-c search_path={SEARCH_PATH}'
        },
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
    },
}

# ---------------------------------------------------------------------------------------
# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa
    },
]

# ---------------------------------------------------------------------------------------
# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# ---------------------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'survey/templates/')]
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')

# ---------------------------------------------------------------------------------------
