import os
from pathlib import Path

# ---------------------------------------------------------------------------------------
# Deployment settings

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = bool(os.getenv('DEBUG', False))

ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    'localhost 127.0.0.1 0.0.0.0'
).split(' ')

SITE_NAME = os.getenv("DJANGO_ADMIN_SITE_NAME", "Application")
SITE_HEADER = os.getenv("SITE_HEADER", SITE_NAME)
SITE_TITLE = os.getenv("SITE_TITLE", SITE_NAME)
INDEX_TITLE = os.getenv("INDEX_TITLE", "Database")

# ---------------------------------------------------------------------------------------
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'tables'
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

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api.wsgi.application'

# ---------------------------------------------------------------------------------------
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASE_ENGINE = os.environ.get(
    'DATABASE_ENGINE',
    'django.db.backends.postgresql'
)
DATABASE_HOST = os.environ.get('DATABASE_HOST', 'sofiax_db')
DATABASE_PORT = os.environ.get('DATABASE_PORT', '5432')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'sofiadb')
DATABASE_USER = os.environ.get('DATABASE_USER', 'admin')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', 'admin')

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,
        'OPTIONS': {
            'options': '-c search_path=public,wallaby'
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

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')

# ---------------------------------------------------------------------------------------
