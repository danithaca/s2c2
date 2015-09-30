import os

from celery import Celery


# set the default Django settings module for the 'celery' program.
# this is necessary to run celery independently to be associated with settings defined in p2.
# see manage.py as well.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'p2.settings')

from django.conf import settings

app = Celery('p2')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
