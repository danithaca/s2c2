from user.models import UserProfile


def current_user_profile(request):
    # This doesn't not add 'current_user_profile' to request.
    # It only adds it to template context.
    # To add 'current_user_profile' in request, use MiddleWare instead.
    # This will override anything in Views handler.
    ctx = {}
    if not hasattr(request, 'current_user_profile') and hasattr(request, 'user') and request.user.is_authenticated():
        ctx['current_user_profile'] = UserProfile(request.user)
    return ctx
