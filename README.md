Servuno Documentation
=================================

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


Promotion piece
-----------------------

Important places for promotion purposes:

  * templates/pages/about.html
  * templates/contract/messages/match_engaged
  * templates/account/new_user_invite


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


Timezone concerns
-----------------

Each user/location is associated with one and only one "area". The area has timezone information.

DayToken/TimeToken do *NOT* care about timezone. They are assumed to be exchangible to textual "tokens", and always agrees with the user's local time. They don't change when Daylight Saving Time changes.

Any DateTimeField needs to care about timezone. They save the exact time something happends.

We use America/Detroit as the default timezone for the backend. In MVP, we don't need to care.


Locations, Classrooms, Centers, Areas, Staff, Managers
------------------------------------------------------

"Area" is like Drupal's organic group. Everything belongs to an area (directly or indirectly).
Centers belong to a single area.
Classrooms belong to a single center.
Managers/Staff belong to one or multiple centers.
Managers have access to all classrooms of the centers they belong to.
Staff are shown in classrooms of all centers.


GIT Branches
----------------------------------

s2c2 related branches:
    * master: the main branch for s2c2 related code in dev (stopped active dev on 2015-08-24, see log)
    * production: the main branch for s2c2 code in production (stopped active dev on 2015-08-24, see log)

p2 related branches:
    * p2dev: the main dev branch for p2 (or servuno), currently maps to v2
    * p2prod: the main prod branch for p2, current maps to v2
    * p2/payment: the branch that evaluates payment options
    * p2/v2: the minimalist design before 3rd pivot (stopped active dev on 2015-09-30)
    * p2/v3: the pivot that targets to parents only


GIT Tags
----------------------------------

New tags:
  * p2-0.1: initial release, before "minimalist design" refactor.
  * p2-0.2: after the minimal design major refactor. changed theme

Outdated, only pertain to s2c2 related stuff:

  * backup-1:   before switching to a customized User model. (update: not going to switch to customized User model. use proxy instead)
  * backup-2:   before switching from customized User model, FullUser, back to Profile pattern. Also not using inheritance for "Group".
  * backup-3:   before using combined regular/date models for slot.
  * backup-4:   about to shrink the number of links and make everything in one big page (with tabs maybe).
  * rel-0.1:    initial offer for children's center
  * rel-0.1.1:  some fix based on rel-0.1
  * rel-0.2:    switched to fullcalendar
  * rel-0.2.1:  a few fixes before adding "message" system.
  * rel-0.3:    added message system
  * rel-0.4:    better assignment (arbitrary assignment)


Log
-----------------------------------

*** 2015-11-04 ***

Ran through the process of creating a new database from scratch. Nothing special to note here. Just run migrate, and then load the fixtures.

Also squashed migrations.


*** 2015-09-30 ***

Now we are using the v3 design that stresses "parents-only" feature and separates parents list and babysitter list. And we don't allow babysitters sign up. This changed a lot from the original s2c2 design and the code will gets a lot of changes. Keeping the s2c2 old code is too much a liability and we are actually removing it in p2/v3 branch. Here is a list of things we will keep:

  * backup of data on production as fixtures.
  * SITE_ID structure: p2 as SITE_ID = 2

The goal is to make the code clean and agile. All old code can be found in the master branch and p2/v2 branch.


*** 2015-08-24 ***

The project started with __s2c2__ (scheduling software for children's center), but gradually moved focus to __p2__ (parents portal) for servuno. The original decision was to keep both s2c2 and p2 codes together in order to reuse code. Now it looks like keeping s2c2 code is more of a liability (preventing code change). The decision now is to remove s2c2 code, but keep the option open to add it back (i.e., keep the SITE_ID structure). This will make p2 more agile to move forward.

Even after code branch break up, both s2c2 and p2 are and will be sharing the same database.

We won't actively remove s2c2 code. The code break up just means that we don't care whether or not code changes to p2 would advertly affect s2c2.