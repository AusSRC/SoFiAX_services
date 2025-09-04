import os
import psycopg2
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------------------
# Deployment settings

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'a0c%$cxr8$(n%y1%ui_ho4nso#%r4)!i^_0ql(1%d)lx!(db10')
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1').split(' ')

# Project specific deployment
LOCAL = os.getenv('LOCAL', True)
DEBUG = os.getenv('DEBUG', True)
PROJECT = os.getenv('PROJECT', 'HI Survey').upper()
BASE_DIR = Path(__file__).resolve().parent.parent

# HTTP stuff
USE_X_FORWARDED_HOST = True
CSRF_TRUSTED_ORIGINS = ['https://*.aussrc.org']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Site
SITE_NAME = os.getenv('SITE_NAME', 'SoFiA web')
SITE_HEADER = os.getenv('SITE_HEADER', 'SoFiA web')
SITE_TITLE = os.getenv('SITE_TITLE', 'SoFiA web')
INDEX_TITLE = os.getenv('INDEX_TITLE', 'SoFiA web')

# Default user
DEFAULT_USER = os.getenv('DJANGO_USERNAME', 'admin')
DEFAULT_PASSWORD = os.getenv('DJANGO_PASSWORD', 'admin')

# Other config
KINEMATICS = os.getenv('KINEMATICS', False)

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

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

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

DATABASE_HOST = os.getenv('DATABASE_HOST', '127.0.0.1')
DATABASE_PORT = os.getenv('DATABASE_PORT', '5432')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'survey')
DATABASE_USER = os.getenv('DATABASE_USER', 'postgres')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'postgres')
SEARCH_PATH = os.getenv('SEARCH_PATH', 'survey')

try:
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
    conn = psycopg2.connect(None, {
        'host': DATABASE_HOST,
        'user': DATABASE_USER,
        'password': DATABASE_PASSWORD,
        'name': DATABASE_NAME,
        'port': DATABASE_PORT,
    })
    conn.close()
except Exception as e:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
    logging.info(os.path.join(BASE_DIR, "db.sqlite3"))

    logging.warning('Database connection failed. Defaulting to sqlite3 database')

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
