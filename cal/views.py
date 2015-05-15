from itertools import groupby, filterfalse
from bootstrapform.templatetags.bootstrap import bootstrap_horizontal
from datetimewidget.widgets import DateWidget
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.views.defaults import bad_request
from django_ajax.decorators import ajax
from django import forms
import re
from location.models import Location, Classroom, Center
from log.models import Log
from s2c2 import settings
from s2c2.decorators import user_check_against_arg, user_is_me_or_same_center, user_classroom_same_center, is_ajax, \
    user_is_center_manager, user_is_verified, user_is_me_or_same_center_manager, user_in_center
from s2c2.templatetags.s2c2_tags import s2c2_icon
from s2c2.utils import dummy, get_fullcaldendar_request_date_range, to_fullcalendar_timestamp, get_request_day, \
    process_messages
from slot.models import OfferSlot, TimeSlot, TimeToken, DayToken, NeedSlot, Meet
from slot import views as slot_views
from user.models import UserProfile, GroupRole, Profile


class StaffTemplateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('template_base_date', 'template_copy_ahead')
        widgets = {
            'template_base_date': DateWidget(bootstrap_version=3, options={
                'daysOfWeekDisabled': '"0,6"',
                'format': 'yyyy-mm-dd',
                'weekStart': 1
            })
        }
        labels = {
            'template_base_date': 'Template week',
            'template_copy_ahead': 'Copy schedule'
        }
        help_texts = {
            'template_base_date': 'Pick a date of which the weekly schedule would be used as the template for automatic copy.'
        }


# permission: myself or verified user from same center.
@login_required
@user_check_against_arg(
    lambda view_user_profile, target_user: target_user is None or view_user_profile.user == target_user or view_user_profile.is_verified() and view_user_profile.is_same_center(target_user),
    lambda args, kwargs: get_object_or_404(User, pk=kwargs['uid']) if 'uid' in kwargs and kwargs['uid'] is not None else None,
    lambda u: UserProfile(u)
)
def calendar_staff(request, uid=None):
    user_profile = UserProfile.get_by_id_default(uid, request.user)
    current_user_profile = UserProfile(request.user)
    day = get_request_day(request)

    staff_copy_form = CopyForm()
    staff_copy_form.fields['current_date'].widget = forms.HiddenInput()

    context = {
        'user_profile': user_profile,
        'day': day,
        'staff_copy_form': staff_copy_form,
        'staff_template_settings_form': StaffTemplateForm(instance=user_profile.profile)
    }

    if user_profile != current_user_profile and current_user_profile.is_center_manager() \
            and current_user_profile.is_verified() and not user_profile.is_verified() \
            and current_user_profile.is_same_center(user_profile):
        # then we allow verify form
        # this form is similar to user:verify()::VerifyForm, but we use IntegerField instead.
        # note that user:verify()::VerifyForm will validate the data using MultipleChoicesField.

        class VerifyForm(forms.Form):
            users = forms.IntegerField(widget=forms.HiddenInput, initial=user_profile.pk)

        context['verify_form'] = VerifyForm()

    return TemplateResponse(request, template='cal/staff.html', context=context)


@ajax(mandatory=False)
@login_required
@user_is_me_or_same_center_manager
def calendar_staff_template(request, uid=None):
    user_profile = UserProfile.get_by_id(uid)
    assert user_profile.is_center_staff()

    if request.method == 'POST':
        form = StaffTemplateForm(request.POST, instance=user_profile.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Template settings updated successfully.')
            return redirect(request.META.get('HTTP_REFERER', reverse('cal:staff', kwargs={'uid': user_profile.user.id})))

    if request.method == 'GET':
        form = StaffTemplateForm(instance=user_profile.profile)

    form_url = reverse('cal:staff', kwargs={'uid': user_profile.user.id})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


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
        special_location_id_set = Location.get_special_list_id_set()
        user_primary_role = user_profile.get_primary_center_role()
        if user_primary_role.machine_name == 'teacher':
            event_color = settings.COLOR_CALENDAR_EVENT_FILLED
        else:
            event_color = settings.COLOR_CALENDAR_EVENT_FILLED_SUBSTITUTE

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
                        if location_id in special_location_id_set:
                            # todo: change settings instead of no url.
                            # event['url'] = reverse('cal:staff_meet', kwargs={'uid': uid})
                            event['color'] = settings.COLOR_CALENDAR_EVENT_SPECIAL
                        else:
                            event['url'] = reverse('cal:classroom', kwargs={'cid': location_id})
                            event['color'] = event_color
                    else:
                        event['title'] = 'Open',
                        event['color'] = settings.COLOR_CALENDAR_EVENT_EMPTY
                        event['url'] = "%s?day=%s&start=%s&end=%s" % (reverse('cal:staff_meet', kwargs={'uid': uid}), DayToken(day).get_token(), TimeToken(time_slot.start).get_token(), TimeToken(time_slot.end).get_token())
                    data.append(event)

        return JsonResponse(data, safe=False)
    else:
        return bad_request(request)


class ClassroomTemplateForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ('template_base_date', 'template_copy_ahead')
        widgets = {
            'template_base_date': DateWidget(bootstrap_version=3, options={
                'daysOfWeekDisabled': '"0,6"',
                'format': 'yyyy-mm-dd',
                'weekStart': 1
            })
        }
        labels = {
            'template_base_date': 'Template week',
            'template_copy_ahead': 'Copy schedule'
        }
        help_texts = {
            'template_base_date': 'Pick a date of which the weekly schedule would be used as the template for automatic copy.'
        }


@login_required
@user_classroom_same_center
def calendar_classroom(request, cid):
    classroom = get_object_or_404(Classroom, pk=cid)
    day = get_request_day(request)

    # handle the modal staff assign form. not used at all now we switch to jquery modal.
    # assign_form = slot_views.AssignForm(classroom, day)

    # handle classroom copy
    classroom_copy_form = CopyForm()
    classroom_copy_form.fields['current_date'].widget = forms.HiddenInput()

    # classroom_copy_day_form = CopyDayForm()

    return render(request, 'cal/classroom.html', {
        'classroom': classroom,
        'day': day,
        # 'assign_form': assign_form,
        'classroom_copy_form': classroom_copy_form,
        'classroom_copy_day_form': CopyDayForm(),
        'classroom_template_settings_form': ClassroomTemplateForm(instance=classroom)
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
                day_token = DayToken(day)
                start_token = TimeToken(time_slot.start)
                end_token = TimeToken(time_slot.end)
                event = {
                    'start': to_fullcalendar_timestamp(day, time_slot.start),
                    'end': to_fullcalendar_timestamp(day, time_slot.end),
                    'id': '%d-%s-%s-%s-%d' % (classroom.pk, DayToken(day).get_token(), TimeToken(time_slot.start).get_token(), TimeToken(time_slot.end).get_token(), user_id or 0)
                }
                if user_id:
                    user_profile = UserProfile.get_by_id(user_id)
                    user_primary_role = user_profile.get_primary_center_role()
                    if user_primary_role.machine_name == 'teacher':
                        event_color = settings.COLOR_CALENDAR_EVENT_FILLED
                    else:
                        event_color = settings.COLOR_CALENDAR_EVENT_FILLED_SUBSTITUTE

                    event['title'] = user_profile.get_display_name()
                    event['color'] = event_color
                    event['url'] = reverse('cal:staff', kwargs={'uid': user_id})
                else:
                    event['title'] = 'Empty'
                    event['color'] = settings.COLOR_CALENDAR_EVENT_EMPTY
                    event['empty'] = True
                    event['url'] = '%s?day=%s&start=%s&end=%s' % (reverse('cal:meet', kwargs={'cid': cid}), day_token.get_token(), start_token.get_token(), end_token.get_token())
                data.append(event)

    return JsonResponse(data, safe=False)


class AssignForm(slot_views.SlotForm):
    #staff = forms.TypedChoiceField(choices=(), label='Available staff', coerce=int, required=True)
    staff = forms.IntegerField(label='Available', widget=forms.Select)

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


class MeetForm(slot_views.SlotForm):
    staff = forms.IntegerField(label='Available', widget=forms.Select, required=False)
    pick = forms.CharField(label='Any', required=False, help_text='Type in name for arbitrary assignment.')
    referer = forms.URLField(required=False, widget=forms.HiddenInput)

    # this is to assign to a particular classroom so 'classroom' is needed.
    # regardless of POST or GET, this will be executed.
    # BUG: if POST and form error (eg: no staff selected), form will have incorrect status.
    def __init__(self, classroom, *args, **kwargs):
        self.classroom = classroom
        day = kwargs.pop('day', None)
        start_time = kwargs.pop('start_time', None)
        end_time = kwargs.pop('end_time', None)
        referer = kwargs.pop('referer', None)
        super(MeetForm, self).__init__(*args, **kwargs)

        # self.fields['day'].widget.attrs['disabled'] = True
        if day:
            self.fields['day'].widget = forms.HiddenInput()
            self.fields['day'].initial = day.get_token()

        # find all staff in the center who are available at the give time period.
        if start_time is not None and end_time is not None:
            list_staff = User.objects.filter(profile__centers=classroom.center, profile__verified=True, offerslot__day=day, offerslot__start_time__gte=start_time, offerslot__end_time__lte=end_time, offerslot__meet__isnull=True).distinct()
            self.fields['start_time'].initial = start_time.get_token()
            self.fields['end_time'].initial = end_time.get_token()
            self.fields['staff'].help_text = 'Available staff between %s and %s. Disabled if none is found.' % (start_time.display(), end_time.display())
        else:
            list_staff = []
            self.fields['staff'].help_text = 'Initial time slot not given. Cannot find available staff.'

        if len(list_staff) == 0:
            self.fields['staff'].widget.attrs['disabled'] = True
        self.fields['staff'].widget.choices = [(0, '- Select -')] + [(u.pk, u.get_full_name() or u.username) for u in list_staff]

        if referer:
            self.fields['referer'].initial = referer

    # here we grab the selected_staff.
    def clean(self):
        cleaned_data = super(MeetForm, self).clean()
        staff_id = cleaned_data.get('staff')
        pick_name = cleaned_data.get('pick')

        if staff_id is None and pick_name is None:
            raise forms.ValidationError('Require at least one staff specified.')

        if pick_name:
            try:
                un = re.match(r'.+ \((.+)\)', pick_name).group(1)
                u = User.objects.get(username=un)
                selected_staff = UserProfile(u)
            except:
                selected_staff = None
                # raise forms.ValidationError('Cannot found typed in staff. Please try again and/or report the error.')
        else:
            try:
                selected_staff = UserProfile.get_by_id(staff_id)
            except:
                selected_staff = None

        if not selected_staff or not selected_staff.is_center_staff():
            raise forms.ValidationError('Selected staff is not valid. Please report the error.')

        cleaned_data['selected_staff'] = selected_staff
        return cleaned_data


@login_required
@user_classroom_same_center
@user_is_center_manager
def meet(request, cid):
    # this is the new view function for classroom assignment.

    classroom = get_object_or_404(Classroom, pk=cid)

    if request.method == 'POST':
        form = MeetForm(classroom, request.POST)

        if form.is_valid():
            day, start_time, end_time = form.get_cleaned_data()
            target_user_profile = form.cleaned_data['selected_staff']
            assigned_list = []

            if 'forced-assign' in form.data:
                # the desired behaviors:
                # 1. if the staff is already assigned somewhere else in any of the given slots, stop and raise an error. we won't handle the case when staff is partially assigned.
                # 2. if the staff is not available at the given slots, create the slots for her.
                # 3. assign the staff so that she takes the exact period.

                # first, test if staff is already assigned somewhere else
                if OfferSlot.objects.filter(user=target_user_profile.user, day=day, start_time__gte=start_time, end_time__lte=end_time, meet__isnull=False).exists():
                    messages.error(request, 'Cannot make assignment because %s is already assigned to another classroom at the time.' % (target_user_profile.get_name()))
                else:
                    # now we know the user doesn't not have any other assignment at the time.
                    # warning: might need to take care of concurrent issues
                    for t in TimeToken.interval(start_time, end_time):
                        need = NeedSlot.objects.filter(location=classroom, day=day, start_time=t, end_time=t.get_next(), meet__isnull=True).first()
                        if need is not None:
                            # this make sure we have an offer that's either created or exists already.
                            offer, created = OfferSlot.objects.get_or_create(user=target_user_profile.user, day=day, start_time=t, end_time=t.get_next())
                            # assert offer.meet is None
                            meet = Meet(offer=offer, need=need)
                            meet.save()
                            assigned_list.append(t)
                            # someday: perhaps we want to send an extra notification too?

            else:
                # business as usual.
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

            referer = form.cleaned_data.get('referer')
            if referer:
                return redirect(referer)
            else:
                return redirect(request.META.get('HTTP_REFERER', reverse('cal:meet', kwargs={'cid': cid})))

    if request.method == 'GET':
        day = get_request_day(request)
        start_time = TimeToken.from_token(request.GET['start']) if 'start' in request.GET else None
        end_time = TimeToken.from_token(request.GET['end']) if 'end' in request.GET else None
        form = MeetForm(classroom, day=day, start_time=start_time, end_time=end_time, referer=request.META.get('HTTP_REFERER'))

    return render(request, 'cal/form_meet.html', {
        'form': form,
        'classroom': classroom
    })


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
                    # need could be empty, now that we enable "shift" delete.
                    if need is not None:
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
    from_field = forms.ChoiceField(choices=(('template', 'Template week'), ('prev', 'last week'), ('curr', 'this week')), label='From')
    to_field = forms.ChoiceField(choices=(('curr', 'this week'), ('next', 'next week')), label='To')
    current_date = forms.CharField()

    def clean(self):
        cleaned_data = super(CopyForm, self).clean()
        from_field = cleaned_data.get("from_field")
        to_field = cleaned_data.get("to_field")
        current_date = cleaned_data.get('current_date')
        if from_field not in ('prev', 'curr', 'template') or to_field not in ('curr', 'next') or from_field == to_field:
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
            elif from_field == 'template':
                if user_profile.profile.template_base_date:
                    from_week = DayToken(user_profile.profile.template_base_date).expand_week()
                else:
                    messages.error(request, 'Template not set')
                    return redirect(request.META.get('HTTP_REFERER', reverse('cal:staff', kwargs={'uid': uid})))
            else:
                assert False

            if to_field == 'curr':
                to_week = current_day.expand_week()
            elif to_field == 'next':
                to_week = current_day.next_week().expand_week()
            else:
                assert False

            if from_week == to_week:
                messages.error(request, 'Cannot copy template to the same week.')
                return redirect(request.META.get('HTTP_REFERER', reverse('cal:staff', kwargs={'uid': uid})))

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
            elif from_field == 'template':
                if classroom.template_base_date:
                    from_week = DayToken(classroom.template_base_date).expand_week()
                else:
                    messages.error(request, 'Template not set')
                    return redirect(request.META.get('HTTP_REFERER', reverse('cal:classroom', kwargs={'cid': classroom.pk})))
            else:
                assert False

            if to_field == 'curr':
                to_week = current_day.expand_week()
            elif to_field == 'next':
                to_week = current_day.next_week().expand_week()
            else:
                assert False

            if from_week == to_week:
                messages.error(request, 'Cannot copy template to the same week.')
                return redirect(request.META.get('HTTP_REFERER', reverse('cal:classroom', kwargs={'cid': classroom.pk})))

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
                messages.warning(request, 'Target date(s) are not copied: %s. Possible reasons: target date(s) not empty or staff is not available.' % ', '.join([d.value.strftime('%b %d') for d in set(failed)]))
            else:
                messages.success(request, 'Copy successful.')

            return redirect(request.META.get('HTTP_REFERER', reverse('cal:classroom', kwargs={'cid': classroom.pk})))

    if request.method == 'GET':
        form = CopyForm()

    form_url = reverse('cal:classroom_copy', kwargs={'cid': classroom.pk})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


class CopyDayForm(forms.Form):
    # this is weird: only showing in the first collapsible panel would the DateWidget work.
    from_field = forms.DateField(label='From', required=True, widget=DateWidget(bootstrap_version=3, options={
        'daysOfWeekDisabled': '"0,6"',
        'format': 'yyyy-mm-dd',
        'weekStart': 1
    }))
    to_field = forms.DateField(label='To', required=True, widget=DateWidget(bootstrap_version=3, options={
        'daysOfWeekDisabled': '"0,6"',
        'format': 'yyyy-mm-dd',
        'weekStart': 1
    }))
    # from_field = forms.DateField(label='From', required=True)
    # to_field = forms.DateField(label='To', required=True)

    def clean(self):
        cleaned_data = super(CopyDayForm, self).clean()
        from_field = cleaned_data.get("from_field")
        to_field = cleaned_data.get("to_field")
        if from_field == to_field:
            raise forms.ValidationError('Cannot copy to itself.')
        return cleaned_data


@ajax(mandatory=False)
@login_required
@user_classroom_same_center
@user_is_center_manager
def calendar_classroom_copy_day(request, cid):
    classroom = get_object_or_404(Classroom, pk=cid)

    if request.method == 'POST':
        # someday: lots of code duplicate as in "calendar_staff_copy".
        form = CopyDayForm(request.POST)
        if form.is_valid():
            from_field = form.cleaned_data["from_field"]
            to_field = form.cleaned_data["to_field"]
            from_day = DayToken(from_field)
            to_day = DayToken(to_field)

            failed = []
            try:
                # copy need.
                NeedSlot.safe_copy(classroom, from_day, to_day)
                # copy meet next. need to be in the same "try", because it should be skipped if NeedSlot copy raises exception.
                Meet.safe_copy_by_location(classroom, from_day, to_day)
            except ValueError as e:
                failed.append(to_day)

            if failed:
                messages.warning(request, 'Target date(s) are not copied: %s. Possible reasons: target date(s) not empty or staff is not available.' % ', '.join([d.value.strftime('%b %d') for d in set(failed)]))
            else:
                messages.success(request, 'Copy successful.')

            return redirect(request.META.get('HTTP_REFERER', reverse('cal:classroom', kwargs={'cid': classroom.pk})))

    if request.method == 'GET':
        form = CopyDayForm()

    form_url = reverse('cal:classroom_copy_day', kwargs={'cid': classroom.pk})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


@ajax(mandatory=False)
@login_required
@user_classroom_same_center
@user_is_center_manager
def calendar_classroom_template(request, cid):
    classroom = get_object_or_404(Classroom, pk=cid)

    if request.method == 'POST':
        form = ClassroomTemplateForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Template settings updated successfully.')
            return redirect(request.META.get('HTTP_REFERER', reverse('cal:classroom', kwargs={'cid': classroom.pk})))

    if request.method == 'GET':
        form = ClassroomTemplateForm(instance=classroom)

    form_url = reverse('cal:classroom_template', kwargs={'cid': classroom.pk})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


@login_required
@user_in_center
def calendar_center(request, cid):
    center = get_object_or_404(Center, pk=cid)
    classroom_color = center.get_classroom_color()

    # sections = [(g.name, g.get_color(), User.objects.filter(profile__centers=center, groups=g.group, is_active=True).order_by("last_name", "first_name", 'username')) for g in (GroupRole.get_by_name(n) for n in ('teacher', 'support', 'intern'))]
    sections = [(g.name, g.get_color(), User.objects.filter(profile__centers=center, groups=g.group, is_active=True).order_by("last_name", "first_name", 'username')) for g in (GroupRole.get_by_name(n) for n in ('teacher', 'support'))]

    context = {
        'center': center,
        'classroom_color_legend': classroom_color,
        'sections': sections
    }
    return render(request, 'cal/center.html', context)


def center_wall_events(cid, fc_start, fc_end):
    search_ref_list = []
    while fc_start != fc_end:
        search_ref_list.append('%d,%s' % (cid, fc_start.get_token()))
        fc_start = fc_start.next_day()

    data = []
    qs = Log.objects.filter(ref__in=search_ref_list, type=Log.COMMENT_BY_LOCATION).values_list('ref', flat=True).distinct()
    for ref in qs:
        day = DayToken.from_token(ref.split(',')[1])
        event = {
            'allDay': True,
            'title': 'Messages posted!',
            'color': 'red',
            'start': day.to_fullcalendar(),
            'url': '%s?day=%s&view=agendaDay' % (reverse('cal:center', kwargs={'cid': cid}), day.get_token()),
        }
        data.append(event)

    return data


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

    # add wall posts event.
    data.extend(center_wall_events(int(cid), start, end))

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


# @is_ajax
# @login_required
# @user_in_center
# def calendar_center_events_available(request, cid):
#     center = get_object_or_404(Center, pk=cid)
#     start, end = get_fullcaldendar_request_date_range(request)
#     data = []
#
#     offer_list = OfferSlot.objects.filter(user__profile__centers=center, user__profile__verified=True, day__range=(start, end), meet__isnull=True).order_by('day', 'start_time', 'user__last_name', 'user__first_name', 'user__username')
#     # step1: group by day
#     for day, group_by_day in groupby(offer_list, lambda x: x.day):
#         # step2: group by half-hour slot
#         group_by_slot = [(t, [o.user for o in g]) for t, g in groupby(group_by_day, lambda x: x.start_time)]
#         # step3: group by joined users
#         for user_list, group_by_user_list in groupby(group_by_slot, lambda x: x[1]):
#             # step4: for each joined users group, group the time slots.
#             for time_slot in TimeSlot.combine([x[0] for x in group_by_user_list]):
#                 event = {
#                     'start': to_fullcalendar_timestamp(day, time_slot.start),
#                     'end': to_fullcalendar_timestamp(day, time_slot.end),
#                     # 'color': color,
#                     'title': ', '.join([u.get_name() for u in user_list]),
#                 }
#                 data.append(event)
#
#     return JsonResponse(data, safe=False)


@is_ajax
@login_required
@user_in_center
def calendar_center_events_available(request, cid):
    center = get_object_or_404(Center, pk=cid)
    start, end = get_fullcaldendar_request_date_range(request)
    data = []

    offer_list = OfferSlot.objects.filter(user__profile__centers=center, user__profile__verified=True, day__range=(start, end), meet__isnull=True).order_by('day', 'user__username', 'start_time')
    # make it a list increase speed in the following when we need to traverse the list multiple times.
    # offer_list = list(offer_list)

    # for role_slug, color in GroupRole.role_color:
    #     # step0: filter by role
    #     if role_slug not in GroupRole.center_staff_roles:
    #         continue
    #     # role_offer_list = filterfalse(lambda o: role_slug in UserProfile(o.user).get_roles_name_set(), offer_list)
    #     role_offer_list = (o for o in offer_list if UserProfile(o.user).get_center_role().role.machine_name == role_slug)

    # step0: group by role
    for role_slug, group_by_role in groupby(offer_list, lambda x: UserProfile(x.user).get_primary_center_role().role.machine_name):
        # step1: group by day
        for day, group_by_day in groupby(group_by_role, lambda x: x.day):
            # step2: group by users
            for user, group_by_user_list in groupby(group_by_day, lambda x: x.user):
                # step3: for each user, group the time slots.
                for time_slot in TimeSlot.combine([x.start_time for x in group_by_user_list]):
                    event = {
                        'start': to_fullcalendar_timestamp(day, time_slot.start),
                        'end': to_fullcalendar_timestamp(day, time_slot.end),
                        'color': GroupRole.role_color_map.get(role_slug, 'darkgray'),
                        'title': user.get_name(),
                        'url': '%s?day=%s' % (reverse('cal:staff', kwargs={'uid': user.id}), day.get_token())
                    }
                    data.append(event)

    return JsonResponse(data, safe=False)


@is_ajax
@login_required
@user_is_me_or_same_center
def calendar_staff_hours(request, uid):
    user_profile = UserProfile.get_by_id(uid)
    day = get_request_day(request)
    if user_profile.is_center_staff():
        # note: .get_week_hours() is in CenterStaff class, not in user_profile in general.
        hours = user_profile.get_week_hours(day)
    else:
        hours = [0, 0, 0]
    return JsonResponse({'total': hours[0], 'work': hours[1], 'empty': hours[2]})


@is_ajax
@login_required
@user_classroom_same_center
def classroom_user_autocomplete(request, cid, template_name='cal/autocomplete.html'):
    classroom = get_object_or_404(Classroom, pk=cid)
    q = request.GET.get('pick', '').strip()
    context = {'q': q}
    queries = {
        'users': User.objects.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q), profile__centers=classroom.center, profile__verified=True, groups__role__machine_name__in=GroupRole.center_staff_roles).distinct()[:3]
    }
    context.update(queries)
    return render(request, template_name, context)


class StaffMeet(slot_views.SlotForm):
    location = forms.ChoiceField(required=True, label='Mark the slot as')
    referer = forms.URLField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        day = kwargs.pop('day', None)
        start_time = kwargs.pop('start_time', None)
        end_time = kwargs.pop('end_time', None)
        referer = kwargs.pop('referer', None)
        super(StaffMeet, self).__init__(*args, **kwargs)

        # self.fields['day'].widget.attrs['disabled'] = True
        if day:
            self.fields['day'].widget = forms.HiddenInput()
            self.fields['day'].initial = day.get_token()

        # find all staff in the center who are available at the give time period.
        if start_time is not None and end_time is not None:
            self.fields['start_time'].initial = start_time.get_token()
            self.fields['end_time'].initial = end_time.get_token()

        if referer:
            self.fields['referer'].initial = referer

        self.fields['location'].choices = [(loc.id, loc.name) for loc in Location.get_special_list()]


@login_required
@user_is_me_or_same_center_manager
def staff_meet(request, uid):
    user_profile = UserProfile.get_by_id(uid)

    if request.method == 'POST':
        form = StaffMeet(request.POST)
        if form.is_valid():
            assigned_list = []
            day, start_time, end_time = form.get_cleaned_data()
            special_location = Location.objects.get(pk=form.cleaned_data['location'])
            for t in TimeToken.interval(start_time, end_time):
                offer = OfferSlot.objects.filter(user=user_profile.user, day=day, start_time=t, end_time=t.get_next(), meet__isnull=True).first()
                need = NeedSlot.get_or_create_unmet_need(location=special_location, day=day, start_time=start_time, end_time=end_time)
                assert offer is not None and need is not None
                meet = Meet(offer=offer, need=need)
                meet.save()
                assigned_list.append(t)

            if len(assigned_list) > 0:
                messages.success(request, 'Assigned slot(s): %s' % TimeSlot.display_combined(assigned_list))
                Log.create(Log.MEET_SPECIAL_UPDATE, request.user, (user_profile.user, special_location, day, assigned_list[0]), 'assigned')
            else:
                messages.warning(request, 'No assignment made due to mismatch between staff availability and classroom needs in the specified time period.')

            referer = form.cleaned_data.get('referer')
            if referer:
                return redirect(referer)
            else:
                return redirect(request.META.get('HTTP_REFERER', reverse('cal:staff_meet', kwargs={'uid': uid})))

    if request.method == 'GET':
        day = get_request_day(request)
        start_time = TimeToken.from_token(request.GET['start']) if 'start' in request.GET else None
        end_time = TimeToken.from_token(request.GET['end']) if 'end' in request.GET else None
        form = StaffMeet(day=day, start_time=start_time, end_time=end_time, referer=request.META.get('HTTP_REFERER'))

    return render(request, 'cal/form_staff_meet.html', {'form': form, 'user_profile': user_profile})
