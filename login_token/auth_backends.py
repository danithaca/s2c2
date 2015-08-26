from django.contrib.auth.backends import ModelBackend
from login_token.models import Token


# according to https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#writing-an-authentication-backend
# the other required method is get_user(user_id), which is already implemented in ModelBackend.
class LoginTokenAuthenticationBackend(ModelBackend):

    def authenticate(self, token=''):
        if not isinstance(token, str) or len(token) != 64:
            return None
        try:
            token_obj = Token.objects.get(token=token)
            if not token_obj.user.is_active:
                return None
            else:
                from django.utils import timezone
                token_obj.accessed = timezone.now()
                token_obj.save()
                return token_obj.user
        except Token.DoesNotExist:
            return None
