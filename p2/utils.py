import json
from datetime import date, time, datetime, timedelta
from enum import Enum
import functools
import sys
import warnings
from braces.views import FormValidMessageMixin, UserPassesTestMixin
from django.contrib import messages

from django.contrib.messages import get_messages
from django.contrib.sites.models import Site
from django.shortcuts import redirect

from django.template.loader import render_to_string
from django.utils import timezone

def get_site_url():
    current_site = Site.objects.get_current()
    return 'http://%s' % current_site.domain


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
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func


class UserRole(Enum):
    PARENT = 7
    SITTER = 8
    HYBRID = 11


class TrustLevel(Enum):
    FULL = 100
    CLOSE = 75
    COMMON = 50
    REMOTE = 25
    NONE = 0
    FORBIDDEN = -100


################# mixin ####################


class RegisteredRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.puser.is_onboard():
            return redirect('tour')
        return super().dispatch(request, *args, **kwargs)


class ControlledFormValidMessageMixin(FormValidMessageMixin):
    show_message = False

    def form_valid(self, form):
        response = super(FormValidMessageMixin, self).form_valid(form)
        if self.show_message and self.get_form_valid_message():
            messages.success(self.request, self.get_form_valid_message(), fail_silently=True)
        return response


# the class that derives this Mixin needs to return True/False about whether the given user is trusted to access the class object.
class TrustedMixin(object):
    def is_user_trusted(self, user, level=TrustLevel.COMMON.value):
        raise NotImplementedError('')


# this doesn't address POST
# class SuccessUrlRedirectMixin(object):
#     redirect_field_name = REDIRECT_FIELD_NAME
#
#     def get_success_url(self):
#         redirect_url = self.request.GET.get(self.redirect_field_name, None)
#         if redirect_url:
#             return redirect_url
#         else:
#             return super().get_success_url()


class ObjectAccessMixin(UserPassesTestMixin):
    raise_exception = True
    trust_level = TrustLevel.COMMON.value
    object_class = None

    def test_func(self, user):
        current_object = self.get_object()
        assert isinstance(current_object, TrustedMixin)
        if self.object_class is not None:
            assert isinstance(current_object, self.object_class)
        return current_object.is_user_trusted(user, self.trust_level)

    def handle_no_permission(self, request):
        messages.error(request, 'You do not have sufficient trust level to access the specified target.')
        return super().handle_no_permission(request)


################ for test purposes ################


class TestEnvMixin(object):
    fixtures = ['area.json', 'signup_code.json', 'sites.json']

    def setUp(self):
        recreate_test_env()


def recreate_test_env():
    from puser.models import PUser, Area
    from circle.models import Friendship
    from contract.models import Contract, Match
    from contract.algorithms import ManualRecommender

    # delete all old users
    PUser.objects.filter(email__in=['test' + s + '@servuno.com' for s in ('', '1', '2', '3', '4', '5')]).delete()

    ###  create users
    t = PUser.create('test@servuno.com', 'password', False)
    t.first_name, t.last_name = 'John', 'Smith'
    t.info.phone = '555-555-5555'
    t.info.note = 'This is a test account.'
    t.save()
    t.info.save()

    t1 = PUser.create('test1@servuno.com', 'password', False)
    t1.first_name, t.last_name = 'Test1', 'Bot'
    t1.info.note = 'This is another test account.'
    t1.save()
    t1.info.save()

    t2 = PUser.create('test2@servuno.com', 'Pa22w0rd', False)
    t2.first_name, t.last_name = 'Nancy', 'Doe'
    t2.is_staff = True
    t2.info.note = 'This is another test account.'
    t2.save()
    t2.info.save()

    # 'test3' is a dummy user to test other things.
    t3 = PUser.create('test3@servuno.com', 'password', dummy=True)

    try:
        another_area = Area.objects.get(name='Seattle')
    except:
        another_area = Area.default()
    t5 = PUser.create('test5@servuno.com', 'password', False, another_area)
    t5.first_name, t.last_name = 'Test5', 'Bot'
    t5.info.note = 'This is a test account home in Seattle.'
    t5.save()
    t5.info.save()

    ### add circles
    f_t_t1 = Friendship(t, t1)
    f_t_t1.activate()
    f_t_t1.approve()

    f_t_t2 = Friendship(t, t2)
    f_t_t2.activate()
    f_t_t2.approve()

    ### add contracts
    current_time = timezone.now()
    t_c = Contract.objects.create(initiate_user=t, area=t.info.area, price=0, event_start=(current_time - timedelta(hours=4)), event_end=(current_time - timedelta(hours=3)), audience_type=Contract.AudienceType.MANUAL.value, audience_data=json.dumps({'users': [t1.id, t2.id]}))

    # this will not work because the contract is already expired.
    # t_c.recommend(initial=True)
    recommender = ManualRecommender(t_c)
    recommender.recommend_initial()

    t_c_m = t_c.match_set.get(target_user=t1)
    t_c_m.accept()
    t_c.confirm(t_c_m)
    t_c.succeed()