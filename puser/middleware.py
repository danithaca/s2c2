from django.utils.functional import SimpleLazyObject

from puser.models import PUser


class PUserMiddleware(object):
    """
    Add puser to all request.
    """

    def process_request(self, request):
        if hasattr(request, 'user'):
            request.puser = SimpleLazyObject(lambda: PUser.from_user(request.user))
            # request.puser = PUser.from_user(request.user)
            # timezone.activate(request.puser.get_timezone())
