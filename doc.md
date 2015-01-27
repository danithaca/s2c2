Development Documentation
=========================

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


Production deployment
---------------------

In settings_local.py:

    * New database settings
    * DEBUG=FALSE, ALLOWED_HOST=...
    * (new SECRET_KEY)


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
