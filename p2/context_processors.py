from django.conf import settings
from puser.models import MenuItem


def global_templates_vars(request):
    ctx = {
        # 'BOOTSTRAP_COLOR_MAPPING': settings.BOOTSTRAP_COLOR_MAPPING,
        'SITE_ID': settings.SITE_ID,
        'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
    }
    try:
        home = MenuItem.objects.get(alias='home', tree__alias='main')
        ctx['breadcrumb_home'] = home
    except MenuItem.DoesNotExist:
        pass
    return ctx
