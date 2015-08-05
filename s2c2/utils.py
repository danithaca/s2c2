import functools
import sys
import re
from datetime import datetime, date, time
import warnings

from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from slot.models import DayToken, TimeToken
from s2c2.decorators import *


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


def get_fullcaldendar_request_date_range(request):
    return DayToken.from_fullcalendar(request.GET['start']), DayToken.from_fullcalendar(request.GET['end'])


def to_fullcalendar_timestamp(d, t):
    # someday: timezone concerns?
    if isinstance(d, DayToken):
        d = d.value
    if isinstance(t, TimeToken):
        t = t.value
    assert isinstance(d, date) and isinstance(t, time)
    dt = datetime.combine(d, t)
    return dt.isoformat()


def get_now():
    return timezone.now()


def process_messages(request):
    """ If messages exist, return the rendered messages string. Otherwise return none. """
    storage = get_messages(request)
    if storage:
        return '\n'.join([render_to_string('includes/message.html', {'message': message}) for message in storage])
    else:
        return None


def is_valid_email(email):
    from django.core.validators import validate_email
    try:
        validate_email(email)
        return True
    except:
        return False


def get_int(s):
    try:
        return int(s)
    except ValueError:
        return 0


def auto_user_name(email):
    """
    Given an email address, generate a random username
    """
    name = email.split('@')[0]
    from django.contrib.auth.models import User
    existing = set(User.objects.filter(username__startswith=name).values_list('username', flat=True))
    if name not in existing:
        return name
    for i in range(1000):
        new_name = '%s%d' % (name, i)
        if new_name not in existing:
            return new_name
    # last resort is to use UUID
    import uuid
    return str(uuid.uuid4())


def deprecated(func):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit(
            "Call to deprecated function {}.".format(func.__name__),
            category=DeprecationWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1
        )
        return func(*args, **kwargs)
    return new_func


# def monkey_patch_django_ajax_render_to_json(response, *args, **kwargs):
#     from django_ajax.shortcuts import logger, Http404, settings, ExceptionReporter, HttpResponseServerError, REASON_PHRASES, JSONResponse
#
#     if hasattr(response, 'status_code'):
#         status_code = response.status_code
#     elif issubclass(type(response), Http404):
#         status_code = 404
#     elif issubclass(type(response), Exception):
#         status_code = 500
#         logger.exception(str(response))
#
#         if settings.DEBUG:
#             import sys
#             reporter = ExceptionReporter(None, *sys.exc_info())
#             text = reporter.get_traceback_text()
#             response = HttpResponseServerError(text, content_type='text/plain')
#         else:
#             response = HttpResponseServerError("An error occured while processing an AJAX request.", content_type='text/plain')
#     else:
#         status_code = 200
#
#     data = {
#         'status': status_code,
#         'statusText': REASON_PHRASES.get(status_code, 'UNKNOWN STATUS CODE'),
#         'content': response
#     }
#
#     # this is the only thing we add here.
#
#     return JSONResponse(data,  *args, **kwargs)
