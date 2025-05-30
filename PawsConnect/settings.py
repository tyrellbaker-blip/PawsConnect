import os
from datetime import timedelta
from datetime import timedelta

from decouple import config

"""
Django settings for PawsConnect project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media/'

GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-*+2&$_=g%xkms5-#1@-*e$6c5vt8h=-w*-nf(uo!#bl*g-k$k)"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'debug_toolbar',
    'django.contrib.gis',
    "Content",
    "PetManagement",
    'UserManagement',
    'rest_framework',
    'rest_framework_gis',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_extensions'
]
AUTH_USER_MODEL = "UserManagement.CustomUser"
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',

]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1982852),  # Access tokens expire after 15 minutes
    'REFRESH_TOKEN_LIFETIME': timedelta(days=151),     # Refresh tokens expire after 1 day
}
ACCOUNT_ADAPTER = 'UserManagement.adapters.CustomAccountAdapter'
SITE_ID = 1

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
GDAL_LIBRARY_PATH = config('GDAL_LIBRARY_PATH')
GEOS_LIBRARY_PATH = config('GEOS_LIBRARY_PATH')

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # Ensure session is available
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Ensure user is authenticated
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    'allauth.account.middleware.AccountMiddleware',
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'debug_toolbar.middleware.DebugToolbarMiddleware',

]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
ROOT_URLCONF = "PawsConnect.urls"

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'paws_reconnect',
        'USER': 'tyrellbaker',
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = "PawsConnect.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 9,
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR / 'static')
]
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('OAUTH_CLIENT_ID'),
            'secret': config('OAUTH_CLIENT_SECRET'),
            'key': ''

        },
        'GOOGLE_AUTH_REDIRECT_URI': config('GOOGLE_AUTH_REDIRECT_URI')
    }
}
LOGIN_REDIRECT_URL = 'UserManagement:profile'
LOGOUT_REDIRECT_URL = 'UserManagement:login'
ACCOUNT_SIGNUP_REDIRECT_URL = 'UserManagement:user_completion'
