from log.models import Notification


def notification_count(request):
    # This doesn't not add 'current_user_profile' to request.
    # It only adds it to template context.
    # To add 'current_user_profile' in request, use MiddleWare instead.
    # This will override anything in Views handler.
    ctx = {}
    if hasattr(request, 'user') and request.user.is_authenticated():
        ctx['notification_count'] = Notification.my_unread_count(request.user)
    return ctx
