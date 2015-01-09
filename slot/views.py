from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from user.models import UserProfile
from .models import RegularSlot, DayOfWeek
import datetime


def _get_request_dow(request):
    """
    Get DOW from request.GET or today's DOW
    """
    if 'dow' in request.GET and int(request.GET['dow']) in RegularSlot.DAY_OF_WEEK_SET:
        return int(request.GET['dow'])
    else:
        return datetime.datetime.today().weekday()


@login_required
def staff_date(request, uid=None):
    user_profile = UserProfile.get_by_id_default(uid, request.user)
    return TemplateResponse(request, template='slot/staff.jinja2', context={
        'user_profile': user_profile
    })


@login_required
def staff_regular(request, uid=None):
    user_profile = UserProfile.get_by_id_default(uid, request.user)
    dow = DayOfWeek(_get_request_dow(request))

    return TemplateResponse(request, template='slot/staff_regular.jinja2', context={
        'user_profile': user_profile,
        'dow': dow,
    })
