import hashlib
import random
from django.core import checks
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


def generate_token(email):
    # copied from account.SignupCode (in hookset.py)
    bits = [email, str(random.SystemRandom().getrandbits(512))]
    return hashlib.sha256("".join(bits).encode("utf-8")).hexdigest()


# we could've use signal to create Token whenver user is created
# but instead we give control to the app to create Token on demand in order to use the "is_user_registered" action.
class Token(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL)
    # used for applications where users might not have explicitly registered yet.
    is_user_registered = models.BooleanField(default=True)
    is_valid = models.BooleanField(default=True)
    token = models.CharField(max_length=64, unique=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    accessed = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def create(user, is_user_registered=True):
        token_string = generate_token(user.email)
        token = Token.objects.create(user=user, is_user_registered=is_user_registered, token=token_string)
        return token


@checks.register()
def login_token_missing_check(app_configs, **kwargs):
    errors = []
    if app_configs is None or 'login_token' in [app.label for app in app_configs]:
        user_model = get_user_model()
        missing = user_model.objects.filter(is_active=True).exclude(token__is_valid=True).count()
        if missing > 0:
            total = user_model.objects.filter(is_active=True).count()
            errors.append(checks.Warning('Users without valid login token: %s/%s' % (missing, total)))
    return errors
