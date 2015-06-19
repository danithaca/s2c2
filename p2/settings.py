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

    # customized
    's2c2',
    'location',
    'user',
    'log',

    'p2',
    'puser',
    'circle',
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

    'puser.middleware.PUserMiddleware',

    # external
    # 'account.middleware.LocaleMiddleware',
    # 'account.middleware.TimezoneMiddleware',
)


TEMPLATE_CONTEXT_PROCESSORS += (
    "account.context_processors.account",
)

# perhaps not needed for now.
# MIDDLEWARE_CLASSES += (
#     "account.middleware.LocaleMiddleware",
#     "account.middleware.TimezoneMiddleware",
# )

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'account.auth_backends.EmailAuthenticationBackend'
)

# from djang-user-account
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
# ACCOUNT_LOGIN_REDIRECT_URL = '/'
# ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL = '/'
ACCOUNT_REMEMBER_ME_EXPIRY = 60 * 60 * 24 * 2       # 2 days

ACCOUNT_USER_DISPLAY = lambda user: user.get_full_name() or user.email


# override login urls
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = reverse_lazy('account_login')
LOGOUT_URL = reverse_lazy('account_logout')


# celery related settings
BROKER_URL = 'sqla+sqlite:///celerydb.sqlite'
CELERY_RESULT_BACKEND = 'db+sqlite:///celerydb.sqlite'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

# load local settings override.

try:
    from p2.settings_local import *
except ImportError:
    if DEBUG:
        logging.warning('p2 local settings not found.')
