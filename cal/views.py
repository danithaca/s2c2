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
from location.models import Location, Classroom, Center
from log.models import Log
from s2c2.decorators import user_check_against_arg, user_is_me_or_same_center, user_classroom_same_center, is_ajax, \
    user_is_center_manager, user_is_verified, user_is_me_or_same_center_manager, user_in_center
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

    staff_copy_form = CopyForm()
    staff_copy_form.fields['current_date'].widget = forms.HiddenInput()

    context = {
        'user_profile': user_profile,
        'day': day,
        'staff_copy_form': staff_copy_form
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
    classroom_copy_form = CopyForm()
    classroom_copy_form.fields['current_date'].widget = forms.HiddenInput()

    return render(request, 'cal/classroom.html', {
        'classroom': classroom,
        'day': day,
        'assign_form': assign_form,
        'classroom_copy_form': classroom_copy_form
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
            day, start_time, end_time = form.get_cleaned_data()
            user_id = int(form.cleaned_data['user_id'])

            if user_id == 0:
                # only delete need. make sure there's no meet assigned.
                for t in TimeToken.interval(start_time, end_time):
                    need = NeedSlot.objects.filter(location=classroom, day=day, start_time=t, end_time=t.get_next(), meet__isnull=True).first()
                    assert need is not None
                    need.delete()
                Log.create(Log.NEED_UPDATE, request.user, (classroom, day), 'deleted %s' % TimeSlot(start_time, end_time))

            else:
                # only delete meet, not need.
                u = User.objects.get(pk=user_id)
                for t in TimeToken.interval(start_time, end_time):
                    need = NeedSlot.objects.filter(location=classroom, day=day, start_time=t, end_time=t.get_next(), meet__offer__user__id=user_id).first()
                    assert need is not None
                    try:
                        need.meet.delete()
                    except Meet.DoesNotExist:
                        assert False
                Log.create(Log.MEET_UPDATE, request.user, (u, classroom, day, start_time))

        return JsonResponse({'success': True})

    return bad_request(request)


class CopyForm(forms.Form):
    from_field = forms.ChoiceField(choices=(('prev', 'last week'), ('curr', 'this week')), label='From')
    to_field = forms.ChoiceField(choices=(('curr', 'this week'), ('next', 'next week')), label='To')
    current_date = forms.CharField()

    def clean(self):
        cleaned_data = super(CopyForm, self).clean()
        from_field = cleaned_data.get("from_field")
        to_field = cleaned_data.get("to_field")
        current_date = cleaned_data.get('current_date')
        if from_field not in ('prev', 'curr') or to_field not in ('curr', 'next') or from_field == to_field:
            raise forms.ValidationError('Cannot copy to itself.')
        if current_date is not None:     # day is required, but will be validated by django after this call
            try:
                d = DayToken.from_token(current_date)
                cleaned_data['current_date'] = d
            except ValueError as e:
                raise forms.ValidationError('Please input a valid day token.')
        return cleaned_data


@ajax(mandatory=False)
@login_required
@user_is_me_or_same_center_manager
def calendar_staff_copy(request, uid):
    user_profile = UserProfile.get_by_id(uid)
    assert user_profile.is_center_staff()

    if request.method == 'POST':
        form = CopyForm(request.POST)
        if form.is_valid():
            from_field = form.cleaned_data["from_field"]
            to_field = form.cleaned_data["to_field"]
            current_day = form.cleaned_data['current_date']

            if from_field == 'prev':
                from_week = current_day.prev_week().expand_week()
            elif from_field == 'curr':
                from_week = current_day.expand_week()
            else:
                assert False

            if to_field == 'curr':
                to_week = current_day.expand_week()
            elif to_field == 'next':
                to_week = current_day.next_week().expand_week()
            else:
                assert False

            failed = []
            assert len(from_week) == len(to_week)
            for from_day, to_day in zip(from_week, to_week):
                assert from_day.weekday() == to_day.weekday()
                try:
                    OfferSlot.safe_copy(user_profile.user, from_day, to_day)
                except ValueError as e:
                    failed.append(to_day)

            if failed:
                messages.warning(request, 'Target day(s) are not empty and cannot be copied to: %s' % ', '.join([d.value.strftime('%b %d') for d in failed]))
            else:
                messages.success(request, 'Copy successful.')

            return redirect(request.META.get('HTTP_REFERER', reverse('cal:staff', kwargs={'uid': uid})))

    if request.method == 'GET':
        form = CopyForm()

    form_url = reverse('cal:staff_copy', kwargs={'uid': uid})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


@ajax(mandatory=False)
@login_required
@user_classroom_same_center
@user_is_center_manager
def calendar_classroom_copy(request, cid):
    classroom = get_object_or_404(Classroom, pk=cid)

    if request.method == 'POST':
        # someday: lots of code duplicate as in "calendar_staff_copy".
        form = CopyForm(request.POST)
        if form.is_valid():
            from_field = form.cleaned_data["from_field"]
            to_field = form.cleaned_data["to_field"]
            current_day = form.cleaned_data['current_date']

            if from_field == 'prev':
                from_week = current_day.prev_week().expand_week()
            elif from_field == 'curr':
                from_week = current_day.expand_week()
            else:
                assert False

            if to_field == 'curr':
                to_week = current_day.expand_week()
            elif to_field == 'next':
                to_week = current_day.next_week().expand_week()
            else:
                assert False

            failed = []
            assert len(from_week) == len(to_week)
            for from_day, to_day in zip(from_week, to_week):
                assert from_day.weekday() == to_day.weekday()
                try:
                    # copy need.
                    NeedSlot.safe_copy(classroom, from_day, to_day)
                    # copy meet next. need to be in the same "try", because it should be skipped if NeedSlot copy raises exception.
                    Meet.safe_copy_by_location(classroom, from_day, to_day)
                except ValueError as e:
                    failed.append(to_day)

            if failed:
                messages.warning(request, 'Target day(s) are not empty and cannot be copied to: %s' % ', '.join([d.value.strftime('%b %d') for d in set(failed)]))
            else:
                messages.success(request, 'Copy successful.')

            return redirect(request.META.get('HTTP_REFERER', reverse('cal:classroom', kwargs={'cid': classroom.pk})))

    if request.method == 'GET':
        form = CopyForm()

    form_url = reverse('cal:classroom_copy', kwargs={'cid': classroom.pk})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


@login_required
@user_in_center
def calendar_center(request, cid):
    center = get_object_or_404(Center, pk=cid)
    classroom_color = center.get_classroom_color()
    context = {
        'center': center,
        'classroom_color_legend': classroom_color
    }
    return render(request, 'cal/center.html', context)


@is_ajax
@login_required
@user_in_center
def calendar_center_events_filled(request, cid):
    center = get_object_or_404(Center, pk=cid)
    classroom_color = center.get_classroom_color()
    start, end = get_fullcaldendar_request_date_range(request)
    data = []

    for classroom, color in classroom_color:
        need_list = NeedSlot.objects.filter(location=classroom, day__range=(start, end), meet__offer__isnull=False).values_list('day', 'start_time', 'meet__offer__user', 'id').order_by('day', 'start_time', 'meet__offer__user__last_name', 'meet__offer__user__first_name', 'meet__offer__user__username')
        # step1: group by day
        for day, group_by_day in groupby(need_list, lambda x: x[0]):
            # step2: group by half-hour slot
            group_by_slot = [(t, [x[2] for x in g]) for t, g in groupby(group_by_day, lambda x: x[1])]
            # step3: group by joined users
            for user_list, group_by_user_list in groupby(group_by_slot, lambda x: x[1]):
                # step4: for each joined users group, group the time slots.
                for time_slot in TimeSlot.combine([TimeToken(x[0]) for x in group_by_user_list]):
                    event = {
                        'start': to_fullcalendar_timestamp(day, time_slot.start),
                        'end': to_fullcalendar_timestamp(day, time_slot.end),
                        'color': color,
                        'title': ', '.join([UserProfile.get_by_id(i).get_display_name() for i in user_list]),
                        'url': reverse('cal:classroom', kwargs={'cid': classroom.id})
                    }
                    data.append(event)

    return JsonResponse(data, safe=False)


@is_ajax
@login_required
@user_in_center
def calendar_center_events_empty(request, cid):
    center = get_object_or_404(Center, pk=cid)
    classroom_color = center.get_classroom_color()
    start, end = get_fullcaldendar_request_date_range(request)
    data = []

    for classroom, color in classroom_color:
        need_list = NeedSlot.objects.filter(location=classroom, day__range=(start, end), meet__offer__isnull=True).values_list('day', 'start_time', 'id').order_by('day', 'start_time')
        # step1: group by day
        for day, group_by_day in groupby(need_list, lambda x: x[0]):
            # step2: group by half-hour slot
            group_by_slot = [(t, len(list(g))) for t, g in groupby(group_by_day, lambda x: x[1])]
            # step3: group by joined users
            for empty_count, group_by_empty_count in groupby(group_by_slot, lambda x: x[1]):
                # step4: for each different empty slot count, group the time slots.
                for time_slot in TimeSlot.combine([TimeToken(x[0]) for x in group_by_empty_count]):
                    event = {
                        'start': to_fullcalendar_timestamp(day, time_slot.start),
                        'end': to_fullcalendar_timestamp(day, time_slot.end),
                        'color': color,
                        'title': 'Empty: %d' % empty_count,
                        'url': reverse('cal:classroom', kwargs={'cid': classroom.id})
                    }
                    data.append(event)

    return JsonResponse(data, safe=False)


@is_ajax
@login_required
@user_is_me_or_same_center
def calendar_staff_hours(request, uid):
    user_profile = UserProfile.get_by_id(uid)
    day = get_request_day(request)
    hours = user_profile.get_week_hours(day)
    return JsonResponse({'total': hours[0], 'work': hours[1], 'empty': hours[2]})