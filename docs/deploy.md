Deployment Settings
==============================


Important info
---------------------------------

Celery command:

```
celery worker -A p2 -l info --autoreload
```

Deploy to Production Checklist:

1. git pull (on production)
2. . /opt/python34/bin/activate
3. ./manage.py collectstatic
4. touch wsgi.py


Production deployment
---------------------

In settings_local.py:

  * New database settings
  * DEBUG=FALSE, ALLOWED_HOST=...
  * (new SECRET_KEY)


Rebuild database
----------------------

1. Run `manage.py migrate`
2. Run `manage.py createsuperuser`
3. Load fixtures
4. Recreate sitetreeload with `--mode=replace` (in order to keep ID)


WSGI Settings
-------------

In http.conf:

    LoadModule wsgi_module modules/mod_wsgi.so
    WSGIPythonHome /opt/python34
    WSGISocketPrefix run/wsgi

In VirtualHost:

    <VirtualHost *:80>
            ServerName s2c2.knowsun.com
            ServerAdmin knowsun@localhost

            WSGIScriptAlias / /home/knowsun/s2c2-prod/s2c2/wsgi.py
            WSGIDaemonProcess s2c2.knowsun.com python-path=/home/knowsun/s2c2-prod:/opt/python34/lib/python3.4/site-packages
            WSGIProcessGroup s2c2.knowsun.com

            Alias /favicon.ico /home/knowsun/s2c2-prod/assets/static

            <Directory /home/knowsun/s2c2-prod/s2c2>
                    <Files wsgi.py>
                            Order allow,deny
                            Allow from all
                    </Files>
            </Directory>

            # note: need trailing slash
            Alias /static/ /home/knowsun/s2c2-prod/assets/static/
            <Directory /home/knowsun/s2c2-prod/assets/static>
                    Order allow,deny
                    Allow from all
            </Directory>

            Alias /media/ /home/knowsun/s2c2-prod/assets/media/
            <Directory /home/knowsun/s2c2-prod/assets/media>
                    Order allow,deny
                    Allow from all
            </Directory>

    </VirtualHost>


Example prod settings_local.py
------------------------------------

```
DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['servuno.com']

EMAIL_BACKEND = 'django_ses_backend.SESBackend'
BROKER_URL = 'django://'

DATABASES = {
    'default': {
        # note: this engine is provided by mysql. the one with django doesn't support py3.
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 's2c2',
        'USER': 's2c2',
        'PASSWORD': 'mercy4me',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 120,     # 2 mins
    }
}

USE_ETAGS = False
CACHE_MIDDLEWARE_SECONDS = -1

```
