from itertools import groupby
from bootstrapform.templatetags.bootstrap import bootstrap_horizontal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.views.defaults import bad_request
from django_ajax.decorators import ajax
from django import forms
from location.models import Location, Classroom
from log.models import Log
from s2c2.decorators import user_check_against_arg, user_is_me_or_same_center, user_classroom_same_center, is_ajax, \
    user_is_center_manager, user_is_verified, user_is_me_or_same_center_manager
from s2c2.templatetags.s2c2_tags import s2c2_icon
from s2c2.utils import dummy, get_fullcaldendar_request_date_range, to_fullcalendar_timestamp, get_request_day, \
    process_messages
from slot.models import OfferSlot, TimeSlot, TimeToken, DayToken, NeedSlot, Meet
from slot import views as slot_views
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
    day = get_request_day(request)
    context = {
        'user_profile': user_profile,
        'day': day,
        'staff_copy_form': CopyForm()
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
                        'end': to_fullcalendar_timestamp(day, time_slot.end),
                        'id': '%d-%s-%s-%s' % (user_profile.pk, DayToken(day).get_token(), TimeToken(time_slot.start).get_token(), TimeToken(time_slot.end).get_token())
                    }
                    if location_id:
                        location = Location.get_by_id(location_id)
                        # event['title'] = s2c2_icon('classroom') + ' ' + location.name
                        event['title'] = location.name
                        event['url'] = reverse('cal:classroom', kwargs={'cid': location_id})
                        event['color'] = 'darkgreen'
                    else:
                        event['title'] = 'Open'
                    data.append(event)

        return JsonResponse(data, safe=False)
    else:
        return bad_request(request)


@login_required
@user_classroom_same_center
def calendar_classroom(request, cid):
    classroom = get_object_or_404(Classroom, pk=cid)
    day = get_request_day(request)
    assign_form = slot_views.AssignForm(classroom, day)

    return render(request, 'cal/classroom.html', {
        'classroom': classroom,
        'day': day,
        'form': assign_form,
    })


@is_ajax
@login_required
@user_classroom_same_center
def calendar_classroom_events(request, cid):
    classroom = get_object_or_404(Classroom, pk=cid)
    start, end = get_fullcaldendar_request_date_range(request)
    data = []

    # note: fullcalendar passes in start/end half inclusive [start, end)
    # note that ForeignKey will be 'id' in values_list().
    need_list = NeedSlot.objects.filter(location=classroom, day__range=(start, end)).values_list('day', 'start_time', 'meet__offer__user', 'id').order_by('day', 'meet__offer__user', 'start_time')
    # first, group by day
    for day, group_by_day in groupby(need_list, lambda x: x[0]):
        # second, group by location
        for user_id, g in groupby(group_by_day, lambda x: x[2]):
            need_slot = list(g)
            for time_slot in TimeSlot.separate_combined([TimeToken(x[1]) for x in need_slot]):
                event = {
                    'start': to_fullcalendar_timestamp(day, time_slot.start),
                    'end': to_fullcalendar_timestamp(day, time_slot.end),
                    'id': '%d-%s-%s-%s-%d' % (classroom.pk, DayToken(day).get_token(), TimeToken(time_slot.start).get_token(), TimeToken(time_slot.end).get_token(), user_id or 0)
                }
                if user_id:
                    user_profile = UserProfile.get_by_id(user_id)
                    event['title'] = user_profile.get_display_name()
                    event['color'] = 'darkgreen'
                    event['url'] = reverse('cal:staff', kwargs={'uid': user_id})
                else:
                    event['title'] = 'Empty'
                    event['empty'] = True
                data.append(event)

    return JsonResponse(data, safe=False)


class AssignForm(slot_views.SlotForm):
    #staff = forms.TypedChoiceField(choices=(), label='Available staff', coerce=int, required=True)
    staff = forms.IntegerField(label='Available staff', widget=forms.Select)

    def __init__(self, classroom, day, start_time, end_time, *args, **kwargs):
        super(AssignForm, self).__init__(*args, **kwargs)
        # find all staff in the center who are available at the give time period.
        if start_time is not None and end_time is not None:
            list_staff = User.objects.filter(profile__centers=classroom.center, profile__verified=True, offerslot__day=day, offerslot__start_time__gte=start_time, offerslot__end_time__lte=end_time, offerslot__meet__isnull=True).distinct()
            self.fields['start_time'].initial = start_time.get_token()
            self.fields['end_time'].initial = end_time.get_token()
        else:
            list_staff = []

        if len(list_staff) == 0:
            self.fields['staff'].widget.attrs['disabled'] = True

        self.fields['staff'].widget.choices = [(0, '- Select -')] + [(u.pk, u.get_full_name() or u.username) for u in list_staff]
        self.fields['day'].widget = forms.HiddenInput()
        self.fields['day'].initial = day.get_token()


@is_ajax
@login_required
@user_classroom_same_center
@user_is_center_manager
def assign(request, cid):
    classroom = get_object_or_404(Classroom, pk=cid)
    day = get_request_day(request)
    start_time = TimeToken.from_token(request.GET.get('start', '0000'))
    end_time = TimeToken.from_token(request.GET.get('end', '2330'))

    if request.method == 'POST':
        form = AssignForm(classroom, day, None, None, request.POST)
        if form.is_valid():
            form_day, start_time, end_time = form.get_cleaned_data()
            assert form_day == day
            assigned_list = []

            target_user_profile = UserProfile.get_by_id(form.cleaned_data['staff'])
            # start assigning
            for t in TimeToken.interval(start_time, end_time):
                offer = OfferSlot.objects.filter(user=target_user_profile.user, day=day, start_time=t, end_time=t.get_next(), meet__isnull=True).first()
                need = NeedSlot.objects.filter(location=classroom, day=day, start_time=t, end_time=t.get_next(), meet__isnull=True).first()
                if offer is not None and need is not None:
                    meet = Meet(offer=offer, need=need)
                    meet.save()
                    assigned_list.append(t)

            if len(assigned_list) > 0:
                messages.success(request, 'Assigned slot(s): %s' % TimeSlot.display_combined(assigned_list))
                Log.create(Log.MEET_UPDATE, request.user, (target_user_profile.user, classroom, day, assigned_list[0]), 'assigned')
            else:
                messages.warning(request, 'No assignment made due to mismatch between staff availability and classroom needs in the specified time period.')

            #data = {'success': True, 'ajax_messages': process_messages(request)}
            data = {'success': True}
            return JsonResponse(data)

    # someday: do not return form html string. instead, return "select" widget options and have all form html already in modal.
    if request.method == 'GET':
        form = AssignForm(classroom, day, start_time, end_time)

    data = {'form': bootstrap_horizontal(form)}
    return JsonResponse(data)


# permission: only verified center manager.
@is_ajax
@login_required
@user_is_verified
@user_is_center_manager
def need_delete_ajax(request, cid):
    classroom = Classroom.objects.get(pk=cid)

    class DeleteFrom(slot_views.SlotForm):
        user_id = forms.IntegerField()

    if request.method == 'POST':
        form = DeleteFrom(request.POST)
        if form.is_valid():
            deleted_time = []
            cascade_delete = {}
            day, start_time, end_time = form.get_cleaned_data()
            user_id = int(form.cleaned_data['user_id'])

            for t in TimeToken.interval(start_time, end_time):
                deleted = False

                # always delete empty needs
                if user_id == 0:
                    need = NeedSlot.objects.filter(location=classroom, day=day, start_time=t, end_time=t.get_next(), meet__isnull=True).first()
                else:
                    need = NeedSlot.objects.filter(location=classroom, day=day, start_time=t, end_time=t.get_next(), meet__offer__user__id=user_id).first()
                if need:
                    try:
                        meet = need.meet
                        #Log.create(Log.MEET_CASCADE_DELETE_NEED, request.user, (meet.offer.user, need.location, need.day, need.start_time))
                        cascade_delete[meet.offer.user] = cascade_delete.get(meet.offer.user, t)      # this only get set once when cascade_delete is none.
                        meet.delete()
                    except Meet.DoesNotExist:
                        pass
                    need.delete()
                    deleted = True

                if deleted:
                    deleted_time.append(t)

            if len(deleted_time) >= 0:
                deleted_message = ', '.join([t.display() for t in TimeSlot.combine(deleted_time)])
                Log.create(Log.NEED_UPDATE, request.user, (classroom, day), 'deleted %s' % deleted_message)
                for u in cascade_delete:
                    Log.create(Log.MEET_CASCADE_DELETE_NEED, request.user, (u, need.location, need.day, need.start_time))

        return JsonResponse({'success': True})

    return bad_request(request)


class CopyForm(forms.Form):
    from_field = forms.ChoiceField(choices=(('prev', 'last week'), ('curr', 'this week')))
    to_field = forms.ChoiceField(choices=(('curr', 'this week'), ('next', 'next week')))
    current_date = forms.DateField()


@login_required
@user_is_me_or_same_center_manager
def calendar_staff_copy(request, uid):
    return redirect(request.META.get('REFERER', '/'))