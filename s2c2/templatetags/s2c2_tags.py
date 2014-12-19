from django import template

register = template.Library()


@register.filter
def bootstrap_alert(message):
    try:
        sub = message.tags if message.tags != 'error' else 'danger'
        return 'alert-%s' % sub
    except Exception:
        return ''