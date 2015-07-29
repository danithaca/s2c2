from django.conf import settings


def global_templates_vars(request):
    ctx = {
        # 'COLOR_MAPPING': settings.bootstrap_color_mapping,
    }
    return ctx
