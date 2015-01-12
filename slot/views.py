from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django import forms
from location.models import Location, Classroom
from log.models import log_offer_regular_update, Log, log_need_regular_update
from s2c2.utils import dummy
from user.models import UserProfile, CenterStaff
from .models import RegularSlot, DayOfWeek, HalfHourTime, OfferRegular, NeedRegular, MeetInfo
from datetime import datetime, time


def _get_request_dow(request):
    """
    Get DOW from request.GET or today's DOW
    """
    if 'dow' in request.GET and int(request.GET['dow']) in RegularSlot.DAY_OF_WEEK_SET:
        return int(request.GET['dow'])
    else:
        return datetime.today().weekday()


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

    if not user_profile.is_center_staff():
        return HttpResponseBadRequest()

    # handle regular offer add form. set data for instance.
    command_form_offer_add = RegularSlotForm()
    command_form_offer_add.fields['start_dow'].widget = forms.HiddenInput()
    command_form_offer_add.fields['start_dow'].initial = dow.dow

    # handle regular offer add form. set data for instance.
    command_form_offer_delete = RegularSlotForm()
    command_form_offer_delete.fields['start_dow'].widget = forms.HiddenInput()
    command_form_offer_delete.fields['start_dow'].initial = dow.dow

    log_entries = Log.objects.filter(type=Log.TYPE_OFFER_REGULAR_UPDATE, ref='%d,%d' % (user_profile.pk, dow.dow)).order_by('-updated')

    return TemplateResponse(request, template='slot/staff_regular.jinja2', context={
        'user_profile': user_profile,
        'dow': dow,
        'slot_table_data': user_profile.get_slot_table_regular(dow.dow),
        'command_form_offer_add': command_form_offer_add,
        'command_form_offer_delete': command_form_offer_delete,
        'change_log_entries': log_entries
    })


class SlotForm(forms.Form):
    start_time = forms.TypedChoiceField(choices=HalfHourTime.get_choices(time(hour=7), time(hour=19, minute=30)),
                                        required=True, coerce=HalfHourTime.parse, label='Start',
                                        initial=HalfHourTime.display(time(hour=9)))
    end_time = forms.TypedChoiceField(choices=HalfHourTime.get_choices(time(hour=7, minute=30), time(hour=20)),
                                      required=True, coerce=HalfHourTime.parse, label='End',
                                      initial=HalfHourTime.display(time(hour=17)))

    def clean(self):
        cleaned_data = super(SlotForm, self).clean()
        t1 = cleaned_data.get("start_time")
        t2 = cleaned_data.get("end_time")

        if t1 is None or t2 is None or t1 >= t2:
            raise forms.ValidationError('End time must be greater than start time.')


class RegularSlotForm(SlotForm):
    # dow = forms.IntegerField(widget=forms.HiddenInput, required=True)
    start_dow = forms.ChoiceField(choices=DayOfWeek.get_choices(), label='Day of week', required=True)


# TODO: add permission
@login_required
def offer_regular_add(request, uid):
    # uid is the target uid, which different from request.user.pk who is the "action" user.
    user_profile = UserProfile.get_by_id(uid)
    assert user_profile.is_center_staff()

    if request.method == 'POST':
        form = RegularSlotForm(request.POST)
        if form.is_valid():
            start_dow = form.cleaned_data['start_dow']
            added_time = OfferRegular.add_interval(start_time=form.cleaned_data['start_time'],
                                          end_time=form.cleaned_data['end_time'],
                                          start_dow=start_dow, user=user_profile.user)
            if len(added_time) == 0:
                messages.warning(request, 'All specified slots are already added. No slot is added again.')
            else:
                messages.success(request, 'Added slot(s): %s' % ', '.join([str(HalfHourTime(t)) for t in added_time]))
                log_offer_regular_update(request.user, user_profile.user, start_dow, 'added slot(s)')
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = RegularSlotForm()

    form_url = reverse('slot:offer_regular_add', kwargs={'uid': uid})
    return render(request, 'base_form.jinja2', {'form': form, 'form_url': form_url, 'uid': uid})


@login_required
def offer_regular_delete(request, uid):
    # uid is the target uid, which different from request.user.pk who is the "action" user.
    user_profile = UserProfile.get_by_id(uid)
    assert user_profile.is_center_staff()

    if request.method == 'POST':
        form = RegularSlotForm(request.POST)
        if form.is_valid():
            start_dow = form.cleaned_data['start_dow']
            if 'delete-all' in form.data:
                deleted = OfferRegular.delete_all(start_dow, user_profile.user)
                if not deleted:
                    messages.warning(request, 'Nothing to delete of the day.')
                else:
                    messages.success(request, 'Delete all day is executed.')
                    log_offer_regular_update(request.user, user_profile.user, start_dow, 'deleted all day')
            else:
                # default 'submit' handler for all other submit button.
                deleted_time = OfferRegular.delete_interval(start_time=form.cleaned_data['start_time'],
                                                            end_time=form.cleaned_data['end_time'],
                                                            start_dow=start_dow, user=user_profile.user)
                if len(deleted_time) == 0:
                    messages.warning(request, 'No available time slot is in the specified time period to delete.')
                else:
                    messages.success(request, 'Deleted slot(s): %s' % ', '.join([str(HalfHourTime(t)) for t in deleted_time]))
                    log_offer_regular_update(request.user, user_profile.user, start_dow, 'deleted slot(s)')
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = RegularSlotForm()

    form_url = reverse('slot:offer_regular_delete', kwargs={'uid': uid})
    return render(request, 'base_form.jinja2', {'form': form, 'form_url': form_url, 'uid': uid})


class NeedRegularSlotForm(RegularSlotForm):
    howmany = forms.ChoiceField(choices=[(i, i) for i in range(1, 6)], label='How many')


@login_required
def classroom_date(request, pk):
    return dummy(request)


@login_required
def classroom_regular(request, pk):
    # lots of code copied from staff_regular()
    try:
        classroom = Classroom.objects.get(pk=pk)
    except Classroom.DoesNotExist as e:
        return HttpResponseBadRequest()
    dow = DayOfWeek(_get_request_dow(request))

    # handle regular need add form
    command_form_need_add = NeedRegularSlotForm()
    command_form_need_add.fields['start_dow'].widget = forms.HiddenInput()
    command_form_need_add.fields['start_dow'].initial = dow.dow

    # handle regular need delete form
    command_form_need_delete = RegularSlotForm()
    command_form_need_delete.fields['start_dow'].widget = forms.HiddenInput()
    command_form_need_delete.fields['start_dow'].initial = dow.dow

    log_entries = Log.objects.filter(type=Log.TYPE_NEED_REGULAR_UPDATE, ref='%d,%d' % (classroom.pk, dow.dow)).order_by('-updated')

    return TemplateResponse(request, template='slot/classroom_regular.jinja2', context={
        'classroom': classroom,
        'dow': dow,
        'command_form_need_add': command_form_need_add,
        'command_form_need_delete': command_form_need_delete,
        'slot_table_data': classroom.get_slot_table_regular(dow.dow),
        'change_log_entries': log_entries,
    })


@login_required
def need_regular_add(request, cid):
    # we don't catch DoesNotExist exception.
    classroom = Classroom.objects.get(pk=cid)

    if request.method == 'POST':
        form = NeedRegularSlotForm(request.POST)
        if form.is_valid():
            start_dow = form.cleaned_data['start_dow']
            NeedRegular.add_interval(start_dow=start_dow, location=classroom,
                                     start_time=form.cleaned_data['start_time'],
                                     end_time=form.cleaned_data['end_time'],
                                     howmany=int(form.cleaned_data['howmany']))
            messages.success(request, 'Needs added.')
            log_need_regular_update(request.user, classroom, start_dow, 'added slot(s)')
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = NeedRegularSlotForm()

    form_url = reverse('slot:need_regular_add', kwargs={'cid': cid})
    return render(request, 'base_form.jinja2', {'form': form, 'form_url': form_url})


@login_required
def need_regular_delete(request, cid):
    classroom = Classroom.objects.get(pk=cid)

    if request.method == 'POST':
        form = RegularSlotForm(request.POST)
        if form.is_valid():
            start_dow = form.cleaned_data['start_dow']
            # fixme: not implemented yet.
            if 'delete-all' in form.data:
                pass
            else:
                # default handler. usually happens when 'delete-empty' is clicked.
                pass
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = RegularSlotForm()

    form_url = reverse('slot:need_regular_delete', kwargs={'cid': cid})
    return render(request, 'base_form.jinja2', {'form': form, 'form_url': form_url})


@login_required
def assign_date(request, need_id):
    return dummy(request)


@login_required
def assign_regular(request, need_id):
    need = get_object_or_404(NeedRegular, pk=need_id)
    time_slot = HalfHourTime(need.start_time)
    # make sure this is a half hour chunk.
    assert time_slot.end_time == need.end_time

    classroom = Classroom.objects.get(pk=need.location.pk)
    main_meet = need.meetregular_set.filter(status=MeetInfo.MAIN).last()

    staff_id_list = OfferRegular.get_staff_id_list(need.start_dow, need.start_time)
    # fixme: add a) 'None' and 'current_staff'
    choices = [(i, UserProfile.get_by_id(i).get_display_name()) for i in staff_id_list]

    class AssignStaffForm(forms.Form):
        staff = forms.ChoiceField(choices=choices, label='Assign available staff')

    if request.method == 'POST':
        form = AssignStaffForm(request.POST)
    if request.method == 'GET':
        form = AssignStaffForm()

    return render(request, 'slot/assign_regular.jinja2', {
        'need': need,
        'time_slot': time_slot,
        'classroom': classroom,
        'main_meet': main_meet,
        'form': form,
    })
