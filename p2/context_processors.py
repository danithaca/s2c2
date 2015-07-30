from django.conf import settings


def global_templates_vars(request):
    ctx = {
        # 'BOOTSTRAP_COLOR_MAPPING': settings.BOOTSTRAP_COLOR_MAPPING,
    }
    return ctx
