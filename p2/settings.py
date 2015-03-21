"""
This file will inherit everything defined in s2c2/settings.py and s2c2/settings-local.py, and override site-related stuff.
"""

from s2c2.settings import *

SITE_ID = 2
ROOT_URLCONF = 'p2.urls'
WSGI_APPLICATION = 'p2.wsgi.application'