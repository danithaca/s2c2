from django.contrib import messages
from django.utils.functional import SimpleLazyObject
from django.conf import settings
from login_token.models import Token
from django.contrib import auth


class LoginTokenMiddleware(object):
    def process_request(self, request):
        token_param = getattr(settings, 'LOGIN_TOKEN_PARAM', 'login_token')
        if token_param in request.GET:
            # now login token is present
            token_string = request.GET[token_param]

            # try:
            #     token_obj = Token.objects.get(token=token_string)
            #
            #     if not token_obj.user.is_active:
            #         messages.error(request, 'The user with the login token is inactive. Cannot login.')
            #         return
            #
            #     if not token_obj.is_valid:
            #         messages.error(request, 'Login token is marked as invalid. Cannot login.')
            #         return
            #
            #     if hasattr(request, 'user') and request.user.is_authenticated():
            #         old_username = request.user.username
            #         auth.logout(request)
            #         messages.info(request, 'Login token presents. Logged out user "%s"' % old_username)
            #
            #     auth.login(request, token_obj.user)
            #     from django.utils import timezone
            #     token_obj.accessed = timezone.now()
            #     token_obj.save()
            #
            # except Token.DoesNotExist:
            #     messages.error(request, 'Login token "%s" is invalid.' % token_string)

            user = auth.authenticate(token=token_string)
            if not user:
                messages.error(request, 'Login token "%s" is invalid or user is inactive.' % token_string)
            else:
                if hasattr(request, 'user') and request.user.is_authenticated() and request.user != user:
                    old_username = request.user.username
                    auth.logout(request)
                    messages.warning(request, 'Login token presents. Logged out user "%s" before login with token.' % old_username)

                auth.login(request, user)
