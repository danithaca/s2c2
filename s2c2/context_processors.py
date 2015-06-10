from django.conf import settings


def global_templates_vars(request):
    ctx = {
        'SITE_ID': settings.SITE_ID,
        'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
    }
    return ctx
