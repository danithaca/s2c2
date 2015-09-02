# this file is for dev. override in prod

import os
import logging
from django.core.urlresolvers import reverse_lazy

################# dev specific ###################

# SECURITY WARNING: don't run with debug turned on in production!
# Don't use this in conditional test in settings because it'll be overriden in production
# Set this to False in settings_local.py in prod
import sys

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nqzos2!&+rri)*rnyodt32uba#alt!!$)0l5x$%-siw6%brub2'


################# application related ###################

SITE_ID = 2
ROOT_URLCONF = 'p2.urls'
WSGI_APPLICATION = 'p2.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # should not use in production
    # 'django_extensions',

    'django.contrib.sites',
    'formtools',

    'localflavor',
    'pytz',
    #'pinax_theme_bootstrap',
    'bootstrapform', # from django-bootstrap-form
    'account',
    'easy_thumbnails',
    'image_cropping',
    'django_ajax',
    'datetimewidget',
    'rest_framework',
    'autocomplete_light',
    #'debug_toolbar',
    #'bootstrap3_datetime',
    'kombu.transport.django',  # for celery
    'djcelery', # for celery
    'login_token',

    # customized
    's2c2',
    'location',
    'user',
    'log',

    'p2',
    'puser',
    # this is to use the AppConfig.
    'circle.apps.CircleConfig',
    'contract',
    'shout',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',

    'login_token.middleware.LoginTokenMiddleware',
    'puser.middleware.PUserMiddleware',

    # external
    # 'account.middleware.LocaleMiddleware',
    # 'account.middleware.TimezoneMiddleware',
)


################# path related ###################


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# content in this directory is not tracked in git.
BASE_DIR_ASSETS = os.path.join(BASE_DIR, 'assets')

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR_ASSETS, 'static')

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# production site should use another folder not in git.
MEDIA_ROOT = os.path.join(BASE_DIR_ASSETS, 'media')
MEDIA_URL = '/media/'


################# services ###################


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}

# celery related settings
BROKER_URL = 'sqla+sqlite:///celerydb.sqlite'
# CELERY_RESULT_BACKEND = 'db+sqlite:///celerydb.sqlite'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

################# email related ####################

DEFAULT_FROM_EMAIL = 'Servuno.com <admin@servuno.com>'
# this will send 500 error report
ADMINS = (('admin', 'danithaca@gmail.com'),)
SERVER_EMAIL = 'Servuno.com <admin@servuno.com>'

EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'logfiles/emails')
AWS_ACCESS_KEY_ID = 'AKIAIK5B54SZPOMAKGMA,'
AWS_SECRET_ACCESS_KEY = 'cdNAyD16yomoHQhwcvQgIniUZa7TLy6a2JDGG+nd'
# AWS_SES_REGION_NAME = 'us-east-1'
# AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'

# use dummy email for dev
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'

# override in settings_local.py
# EMAIL_BACKEND = 'django_ses_backend.SESBackend'

################# i18n/l10n/datetime ###################

LANGUAGE_CODE = 'en-us'
# this only applies to rendering whit USE_TZ is True.
TIME_ZONE = 'America/Detroit'
# TIME_ZONE = 'UTC'
USE_I18N = False  # True
USE_L10N = True  # True
# This makes django save datetime in UTC.
USE_TZ = True
TIME_FORMAT = 'h:iA'

# make sure to be consistent to the javascript util function.
DATETIME_INPUT_FORMATS = (
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'

    '%Y-%m-%d %I:%M%p',      # '2006-10-25 02:30PM'
    '%m/%d/%Y %I:%M%p',      # '10/25/2006 02:30PM'
)

################# user related ###################

# AUTH_USER_MODEL = 'puser.PUser'
AUTH_USER_MODEL = 'auth.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'account.auth_backends.EmailAuthenticationBackend',
    # this is the login token backend.
    'login_token.auth_backends.LoginTokenAuthenticationBackend',
)

# from djang-user-account
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = False
ACCOUNT_SIGNUP_REDIRECT_URL = 'onboard_start'  # this is URLConf, not str.
# ACCOUNT_LOGIN_REDIRECT_URL = '/'
# ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL = '/'
ACCOUNT_REMEMBER_ME_EXPIRY = 60 * 60 * 24 * 2  # 2 days
# if needed, we could override hookset to use celery for sending emails
# ACCOUNT_HOOKSET =
ACCOUNT_USER_DISPLAY = lambda user: user.get_full_name() or user.email
ACCOUNT_CREATE_ON_SAVE = True  # default. automatically create "Account"/"EmailAddress" when user object is created.
ACCOUNT_LANGUAGES = (
    ('en-us', 'English - US'),
)

# override login urls
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = reverse_lazy('account_login')
LOGOUT_URL = reverse_lazy('account_logout')


################# loggin ###################

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logfiles/debug.log'),
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            # 'stream': sys.stdout,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}


################# template/UI ###################

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",

    # add 'request' in context, which can be accessed from within template.
    'django.core.context_processors.request',
    # 'pinax_theme_bootstrap.context_processors.theme',
    # 'account.context_processors.account',

    # for all templates
    's2c2.context_processors.global_templates_vars',
    # add 'user_profile' to request
    'user.context_processors.current_user_profile',
    # add notification count
    'log.context_processors.notification_count',

    'account.context_processors.account',
    'p2.context_processors.global_templates_vars',
)

# for thumbnail processing.
from easy_thumbnails.conf import Settings as thumbnail_settings

THUMBNAIL_PROCESSORS = ('image_cropping.thumbnail_processors.crop_corners',) + thumbnail_settings.THUMBNAIL_PROCESSORS

# IMAGE_CROPPING_JQUERY_URL = 'https://code.jquery.com/jquery-2.1.3.min.js'
IMAGE_CROPPING_THUMB_SIZE = (400, 400)
IMAGE_CROPPING_SIZE_WARNING = True

# remove green (clashes with other calendar colors), gray, black
COLORS = ['maroon',
          'navy',
          'red',
          'teal',
          'blue',
          'orange',
          'yellowgreen',
          'aqua',
          'purple',
          'fuchsia',
          'lime',
          'olive']

COLOR_CALENDAR_EVENT_EMPTY = 'gray'
COLOR_CALENDAR_EVENT_FILLED = 'darkgreen'
COLOR_CALENDAR_EVENT_FILLED_SUBSTITUTE = 'tomato'
COLOR_CALENDAR_EVENT_SPECIAL = 'black'
COLOR_MANAGER = 'tomato'
COLOR_STAFF = 'darkgreen'
COLOR_STAFF_SUBSTITUTE = 'tomato'

# this is mapped from bootstrap paper theme: https://bootswatch.com/paper/
BOOTSTRAP_COLOR_MAPPING = {
    'default': '#e6e6e6',
    'primary': '#0c7cd5',
    'success': '#3d8b40',
    'warning': '#ff9800',
    'danger': '#cb171e',
    'info': '#771e86',
}


################## import local settings ###################

try:
    from p2.settings_local import *
except ImportError:
    logging.warning('local settings not found.')
