from django.conf import settings


def global_templates_vars(request):
    ctx = {
        'site_id': settings.SITE_ID
    }
    return ctx
