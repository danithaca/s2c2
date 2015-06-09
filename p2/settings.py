"""
This file will inherit everything defined in s2c2/settings.py and s2c2/settings-local.py, and override site-related stuff.
"""

from s2c2.settings import *

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

    'localflavor',
    'pytz',
    'pinax_theme_bootstrap',
    'bootstrapform', # from django-bootstrap-form
    'account',
    'easy_thumbnails',
    'image_cropping',
    'django_ajax',
    'datetimewidget',
    'rest_framework',
    'autocomplete_light',
    #'debug_toolbar',

    # customized
    's2c2',
    'location',
    'user',
    'log',

    'p2',
    'puser',
    'circle',
    'contract',
)


# load local settings override.

try:
    from p2.settings_local import *
except ImportError:
    if DEBUG:
        logging.warning('p2 local settings not found.')
