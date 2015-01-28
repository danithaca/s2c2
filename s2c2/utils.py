import sys
from django.http import HttpResponse
from slot.models import DayToken
from s2c2.decorators import *
from django.utils import timezone


@user_check_against_arg(lambda x, y: y is None or x.username == y, lambda args, kwargs: kwargs.get('message', None))
@user_is_verified
def dummy(request, message='Please override.'):
    # p = request.user_profile
    # message = 'User name: %s' % p.get_full_name()
    return HttpResponse(message)
    # return render(request, 'snippet/command_form.html')


def get_class(class_name):
    """
    This function gets the class from a string "class_name".
    See: http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
    :param class_name: the string of the class name
    :return: the "class" object so you can instantiate it.
    """
    parts = class_name.split('.')
    if len(parts) > 1:
        # that is, we need to import the module first.
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
    else:
        # assuming the class is already in scope
        return getattr(sys.modules['__main__'], class_name)


def get_request_day(request):
    try:
        day = DayToken.from_token(request.GET.get('day', ''))
    except ValueError as e:
        day = DayToken.today()
    return day


def get_now():
    return timezone.now()