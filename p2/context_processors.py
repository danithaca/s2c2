from django.conf import settings
from puser.models import MenuItem


def global_templates_vars(request):
    ctx = {
        # 'BOOTSTRAP_COLOR_MAPPING': settings.BOOTSTRAP_COLOR_MAPPING,
        'SITE_ID': settings.SITE_ID,
        'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
    }
    # try:
    #     if request.user.is_authenticated():
    #         home = MenuItem.objects.get(alias='home', tree__alias='main')
    #     else:
    #         home = MenuItem.objects.get(alias='home', tree__alias='prelogin')
    #     ctx['breadcrumb_home'] = home
    # except MenuItem.DoesNotExist:
    #     pass
    return ctx
