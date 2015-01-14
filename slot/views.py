from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest
from django.views import defaults
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django import forms
from location.models import Location, Classroom
from log.models import Log, log_offer_update, log_need_update
from s2c2.utils import dummy
from user.models import UserProfile, CenterStaff
from .models import RegularSlot, DayOfWeek, HalfHourTime, OfferRegular, NeedRegular, MeetInfo, DayToken, TimeToken, \
    OfferSlot, NeedSlot, MeetSlot
from datetime import datetime, time


def _get_request_day(request):
    try:
        day = DayToken.from_token(request.GET.get('day', ''))
    except ValueError as e:
        day = DayToken.today()
    return day


@login_required
def day_staff(request, uid=None):
    user_profile = UserProfile.get_by_id_default(uid, request.user)
    if not user_profile.is_center_staff():
        return defaults.bad_request(request)
    day = _get_request_day(request)

    slot_table_data = user_profile.get_slot_table(day)

    # handle offer add form. set date for instance.
    command_form_offer_add = SlotForm()
    command_form_offer_add.fields['day'].widget = forms.HiddenInput()
    command_form_offer_add.fields['day'].initial = day.get_token()

    # handle offer delete form. set date for instance.
    command_form_offer_delete = SlotForm()
    command_form_offer_delete.fields['day'].widget = forms.HiddenInput()
    command_form_offer_delete.fields['day'].initial = day.get_token()

    log_entries = Log.objects.filter(type=Log.TYPE_OFFER_UPDATE, ref='%d,%s' % (user_profile.pk, day.get_token())).order_by('-updated')

    return render(request, 'slot/staff.jinja2', {
        'user_profile': user_profile,
        'day': day,
        'slot_table_data': slot_table_data,
        'command_form_offer_add': command_form_offer_add,
        'command_form_offer_delete': command_form_offer_delete,
        'change_log_entries': log_entries,
    })


class SlotForm(forms.Form):
    start_time = forms.TypedChoiceField(choices=TimeToken.get_choices(time(7), time(19, 30)),
                                        required=True, coerce=TimeToken.from_token, label='Start',
                                        initial=TimeToken(time(9)).get_token())
    end_time = forms.TypedChoiceField(choices=TimeToken.get_choices(time(7, 30), time(20)),
                                      required=True, coerce=TimeToken.from_token, label='End',
                                      initial=TimeToken(time(17)).get_token())
    day = forms.CharField(label='Day', required=True)

    def clean(self):
        cleaned_data = super(SlotForm, self).clean()
        t1 = cleaned_data.get("start_time")
        t2 = cleaned_data.get("end_time")
        day = cleaned_data.get('day')
        if t1 is not None and t2 is not None and t1 >= t2:
            raise forms.ValidationError('End time must be greater than start time.')
        if day is not None:     # day is required, but will be validated by django after this call
            try:
                DayToken.from_token(day)
            except ValueError as e:
                raise forms.ValidationError('Please input a valid day token.')
        return cleaned_data

    # call only after is_valid().
    def get_cleaned_data(self):
        day = DayToken.from_token(self.cleaned_data['day'])
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']
        return day, start_time, end_time


class NeedSlotForm(SlotForm):
    howmany = forms.ChoiceField(choices=[(i, i) for i in range(1, 6)], label='How many', initial=1)

    def get_cleaned_data(self):
        day, start_time, end_time = super(NeedSlotForm, self).get_cleaned_data()
        return day, start_time, end_time, int(self.cleaned_data['howmany'])


# TODO: add permission
@login_required
def offer_add(request, uid):
    # uid is the target uid, which different from request.user.pk who is the "action" user.
    user_profile = UserProfile.get_by_id(uid)
    assert user_profile.is_center_staff()

    if request.method == 'POST':
        form = SlotForm(request.POST)
        if form.is_valid():
            added_time = []
            day = DayToken.from_token(form.cleaned_data['day'])
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            # add offer slot
            for t in TimeToken.interval(start_time, end_time):
                added = OfferSlot.add_missing(day, user_profile.user, t)
                if added:
                    added_time.append(t)

            if len(added_time) == 0:
                messages.warning(request, 'All specified slots are already added. No slot is added again.')
            else:
                messages.success(request, 'Added slot(s): %s' % ', '.join([t.display_slice() for t in added_time]))
                log_offer_update(request.user, user_profile.user, day, 'added slot(s)')
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = SlotForm()

    form_url = reverse('slot:offer_add', kwargs={'uid': uid})
    return render(request, 'base_form.jinja2', {'form': form, 'form_url': form_url})


@login_required
def offer_delete(request, uid):
    # uid is the target uid, which different from request.user.pk who is the "action" user.
    user_profile = UserProfile.get_by_id(uid)
    assert user_profile.is_center_staff()

    if request.method == 'POST':
        form = SlotForm(request.POST)
        if form.is_valid():
            deleted_time = []
            day = DayToken.from_token(form.cleaned_data['day'])
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            if 'delete-all' in form.data:
                deleted = OfferSlot.delete_all(day, user_profile.user)
                if not deleted:
                    messages.warning(request, 'Nothing to delete of the day.')
                else:
                    messages.success(request, 'Delete all day is executed.')
                    log_offer_update(request.user, user_profile.user, day, 'deleted all day')
            else:
                # default 'submit' handler for all other submit button.
                for t in TimeToken.interval(start_time, end_time):
                    deleted = OfferSlot.delete_existing(day, user_profile.user, t)
                    if deleted:
                        deleted_time.append(t)

                if len(deleted_time) == 0:
                    messages.warning(request, 'No available time slot is in the specified time period to delete.')
                else:
                    messages.success(request, 'Deleted slot(s): %s' % ', '.join([t.display_slice() for t in deleted_time]))
                    log_offer_update(request.user, user_profile.user, day, 'deleted slot(s)')
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = SlotForm()

    form_url = reverse('slot:offer_delete', kwargs={'uid': uid})
    return render(request, 'base_form.jinja2', {'form': form, 'form_url': form_url})


@login_required
def day_classroom(request, cid):
    # lots of code copied from staff()
    classroom = get_object_or_404(Classroom, pk=cid)
    day = _get_request_day(request)

    slot_table_data = classroom.get_slot_table(day)

    # handle regular need add form
    command_form_need_add = NeedSlotForm()
    command_form_need_add.fields['day'].widget = forms.HiddenInput()
    command_form_need_add.fields['day'].initial = day.get_token()

    # handle regular need delete form
    command_form_need_delete = SlotForm()
    command_form_need_delete.fields['day'].widget = forms.HiddenInput()
    command_form_need_delete.fields['day'].initial = day.get_token()

    log_entries = Log.objects.filter(type=Log.TYPE_NEED_UPDATE, ref='%d,%s' % (classroom.pk, day.get_token())).order_by('-updated')

    return TemplateResponse(request, template='slot/classroom.jinja2', context={
        'classroom': classroom,
        'day': day,
        'command_form_need_add': command_form_need_add,
        'command_form_need_delete': command_form_need_delete,
        'slot_table_data': slot_table_data,
        'change_log_entries': log_entries,
    })


@login_required
def need_add(request, cid):
    # we don't catch DoesNotExist exception.
    classroom = Classroom.objects.get(pk=cid)

    if request.method == 'POST':
        form = NeedSlotForm(request.POST)
        if form.is_valid():
            day, start_time, end_time, howmany = form.get_cleaned_data()
            for t in TimeToken.interval(start_time, end_time):
                for i in range(howmany):
                    m = NeedSlot(location=classroom, day=day, start_time=t, end_time=t.get_next())
                    m.save()
            messages.success(request, 'Needs added.')
            log_need_update(request.user, classroom, day, 'added slot(s)')
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = NeedSlotForm()

    form_url = reverse('slot:need_add', kwargs={'cid': cid})
    return render(request, 'base_form.jinja2', {'form': form, 'form_url': form_url})


@login_required
def need_delete(request, cid):
    classroom = Classroom.objects.get(pk=cid)

    if request.method == 'POST':
        form = SlotForm(request.POST)
        if form.is_valid():
            day, start_time, end_time = form.get_cleaned_data()
            # fixme: not implemented yet.
            if 'delete-all' in form.data:
                pass
            else:
                # default handler. usually happens when 'delete-empty' is clicked.
                pass
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = SlotForm()

    form_url = reverse('slot:need_delete', kwargs={'cid': cid})
    return render(request, 'base_form.jinja2', {'form': form, 'form_url': form_url})


@login_required
def assign(request, need_id):
    return dummy(request)
    # need = get_object_or_404(NeedSlot, pk=need_id)
    # # make sure start_time and end_time is right.
    # assert need.start_time.get_next() == need.end_time
    #
    # classroom = Classroom.objects.get(pk=need.location.pk)
    # main_meet = need.meetslot_set.filter(status=MeetSlot.MAIN).last()
    #
    # staff_id_list = OfferRegular.get_staff_id_list(need.start_dow, need.start_time)
    # # fixme: add a) 'None' and 'current_staff'
    # choices = [(i, UserProfile.get_by_id(i).get_display_name()) for i in staff_id_list]
    #
    # class AssignStaffForm(forms.Form):
    #     staff = forms.ChoiceField(choices=choices, label='Assign available staff')
    #
    # if request.method == 'POST':
    #     form = AssignStaffForm(request.POST)
    # if request.method == 'GET':
    #     form = AssignStaffForm()
    #
    # return render(request, 'slot/assign.jinja2', {
    #     'need': need,
    #     'time_slot': time_slot,
    #     'classroom': classroom,
    #     'main_meet': main_meet,
    #     'form': form,
    # })
