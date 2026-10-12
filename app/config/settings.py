import os
import environ
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables, from the .env file in the root of the repository when the
# application is run locally (or the file in ENV_FILE). In Docker they are set by docker-compose.
env = environ.Env()
environ.Env.read_env(os.environ.get("ENV_FILE", BASE_DIR.parent / ".env"))

# ---------------------------------------------------------------------------------------
# Deployment settings

PROJECT = env("PROJECT")
if not PROJECT:
    raise Exception("Project not defined")

PROJECT = PROJECT.upper()

# Modules of the application to install (app/modules), in the order they are loaded
AVAILABLE_MODULES = ["core", "operations", "wallaby", "dingo"]
# Names of the modules before the application was restructured
MODULE_ALIASES = {
    "metadata": "core",
    "wallaby_operations": "wallaby",
    "wallaby_kinematics": "wallaby",
    "dingo_gama": "dingo",
}
_modules = [MODULE_ALIASES.get(m.strip(), m.strip()) for m in env("MODULES").split(",") if m.strip()]
_unknown = [m for m in _modules if m not in AVAILABLE_MODULES]
if _unknown:
    raise ImproperlyConfigured(f"MODULES: unknown module {', '.join(_unknown)}")
MODULES = [m for m in AVAILABLE_MODULES if m in _modules]
if "core" not in MODULES:
    raise ImproperlyConfigured("MODULES: core is required")
if "wallaby" in MODULES and "operations" not in MODULES:
    raise ImproperlyConfigured("MODULES: wallaby requires operations")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
USE_X_FORWARDED_HOST = True
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["https://*.aussrc.org"])

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default="localhost 127.0.0.1").split(" ")
SITE_NAME = env("SITE_NAME", default=f"{PROJECT} Catalog")
SITE_HEADER = env("SITE_HEADER", default=SITE_NAME)
SITE_TITLE = env("SITE_TITLE", default=SITE_NAME)
INDEX_TITLE = env("INDEX_TITLE", default=SITE_NAME)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Detections below these thresholds are not shown in the admin pages or manual inspection (0 to disable)
DETECTION_MIN_N_PIX = env.int("DETECTION_MIN_N_PIX", default=300)
DETECTION_MIN_REL = env.float("DETECTION_MIN_REL", default=0.7)

# CARTA server to open the image cube of a detection from the manual inspection page (optional)
CARTA_URL = env("CARTA_URL", default=None)

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ]
}

# ---------------------------------------------------------------------------------------
# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "sslserver",
    "django_extensions",
    *[f"modules.{module}" for module in MODULES],
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------------------
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# The defaults are those of the database created by server/db (make db)
DATABASE_HOST = env("DATABASE_HOST", default="localhost")
DATABASE_PORT = env("DATABASE_PORT", default="5432")
DATABASE_NAME = env("DATABASE_NAME", default="surveydb")
DATABASE_USER = env("DATABASE_USER", default=env("DATABASE_ADMIN_USERNAME", default="admin"))
DATABASE_PASSWORD = env("DATABASE_PASSWORD", default=env("DATABASE_ADMIN_PASSWORD", default=None))
SEARCH_PATH = env("SEARCH_PATH", default=f"{env('DATABASE_SCHEMA', default='survey')},public")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {"options": f"-c search_path={SEARCH_PATH}"},
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "PORT": DATABASE_PORT,
    },
}

# ---------------------------------------------------------------------------------------
# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa
    },
]

# ---------------------------------------------------------------------------------------
# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# ---------------------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media")

# ---------------------------------------------------------------------------------------
