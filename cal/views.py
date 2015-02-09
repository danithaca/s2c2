from itertools import groupby
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.views.defaults import bad_request
from django_ajax.decorators import ajax
from location.models import Location
from s2c2.decorators import user_check_against_arg, user_is_me_or_same_center
from s2c2.templatetags.s2c2_tags import s2c2_icon
from s2c2.utils import dummy, get_fullcaldendar_request_date_range, to_fullcalendar_timestamp
from slot.models import OfferSlot, TimeSlot, TimeToken
from user.models import UserProfile


# permission: myself or verified user from same center.
@login_required
@user_check_against_arg(
    lambda view_user_profile, target_user: target_user is None or view_user_profile.user == target_user or view_user_profile.is_verified() and view_user_profile.is_same_center(target_user),
    lambda args, kwargs: get_object_or_404(User, pk=kwargs['uid']) if 'uid' in kwargs and kwargs['uid'] is not None else None,
    lambda u: UserProfile(u)
)
def calendar_staff(request, uid=None):
    user_profile = UserProfile.get_by_id_default(uid, request.user)
    context = {
        'user_profile': user_profile,
        }
    return TemplateResponse(request, template='cal/staff.html', context=context)


@login_required
@user_check_against_arg(
    lambda view_user_profile, target_user: view_user_profile.user == target_user or view_user_profile.is_verified() and view_user_profile.is_same_center(target_user),
    lambda args, kwargs: get_object_or_404(User, pk=kwargs['uid']),
    lambda u: UserProfile(u)
)
def calendar_staff_events(request, uid):
    """ ajax response """
    if request.is_ajax():
        user_profile = UserProfile.get_by_id(uid)
        start, end = get_fullcaldendar_request_date_range(request)
        data = []

        # note: fullcalendar passes in start/end half inclusive [start, end)
        # note that ForeignKey will be 'id' in values_list().
        offer_list = OfferSlot.objects.filter(user=user_profile.user, day__range=(start, end)).values_list('day', 'start_time', 'meet__need__location').order_by('day', 'meet__need__location', 'start_time')
        # first, group by day
        for day, group_by_day in groupby(offer_list, lambda x: x[0]):
            # second, group by location
            for location_id, g in groupby(group_by_day, lambda x: x[2]):
                for time_slot in TimeSlot.combine([TimeToken(x[1]) for x in g]):
                    event = {
                        'start': to_fullcalendar_timestamp(day, time_slot.start),
                        'end': to_fullcalendar_timestamp(day, time_slot.end)
                    }
                    if location_id:
                        location = Location.get_by_id(location_id)
                        # event['title'] = s2c2_icon('classroom') + ' ' + location.name
                        event['title'] = location.name
                        event['url'] = reverse('cal:classroom', kwargs={'cid': location_id})
                    else:
                        event['title'] = 'Open'
                        event['color'] = 'gray'
                    data.append(event)

        return JsonResponse(data, safe=False)
    else:
        return bad_request(request)


def calendar_classroom(request, cid):
    return dummy(request)