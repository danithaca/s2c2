from datetime import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db import connection
from django.views import defaults
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django import forms

from location.models import Classroom
from log.models import Log
from s2c2.utils import get_request_day
from user.models import UserProfile
from .models import DayToken, TimeToken, OfferSlot, NeedSlot, Meet, TimeSlot
from s2c2.decorators import *


# required permission: logged user, verified users from same center or myself
# we only allow view different user's profile if the viewing user is verified and belongs to the same center as the viewed user.
@login_required
@user_check_against_arg(
    lambda view_user, target_user: target_user is None or view_user == target_user or (UserProfile(view_user).is_verified() and (UserProfile(view_user).is_same_center(target_user))),
    lambda args, kwargs: get_object_or_404(User, pk=kwargs['uid']) if 'uid' in kwargs else None
)
def day_staff(request, uid=None):
    user_profile = UserProfile.get_by_id_default(uid, request.user)
    if not user_profile.is_center_staff():
        return defaults.bad_request(request)
    day = get_request_day(request)

    # check permission: (use decorator instead)
    # if user_profile.user != request.user and not (user_profile.is_same_center(request.user) and UserProfile(request.user).is_verified()):
    #     return defaults.permission_denied(request)

    slot_table_data = user_profile.get_slot_table(day)
    unmet_table_data = user_profile.get_unmet_table(day)

    # handle offer add form. set date for instance.
    command_form_offer_add = SlotForm()
    command_form_offer_add.fields['day'].widget = forms.HiddenInput()
    command_form_offer_add.fields['day'].initial = day.get_token()

    # handle offer delete form. set date for instance.
    command_form_offer_delete = SlotForm()
    command_form_offer_delete.fields['day'].widget = forms.HiddenInput()
    command_form_offer_delete.fields['day'].initial = day.get_token()

    # copy form
    command_form_copy = DayForm()
    command_form_copy.fields['day'].widget = forms.HiddenInput()
    command_form_copy.fields['day'].initial = day.get_token()

    db_regex = (r'^%d,[0-9]+,%s,[0-9]+$' if connection.vendor == 'mysql' else r'^%d,[0-9]+,%s,[0-9]+$') % (user_profile.pk, day.get_token())
    q = Q(ref='%d,%s' % (user_profile.pk, day.get_token())) | Q(ref__regex=db_regex)
    log_entries = Log.objects.filter(q, type__in=(Log.OFFER_UPDATE, Log.TEMPLATE_OP_STAFF, Log.MEET_UPDATE, Log.MEET_CASCADE_DELETE_NEED)).order_by('-updated')[:20]

    return render(request, 'slot/staff.html', {
        'user_profile': user_profile,
        'day': day,
        'slot_table_data': slot_table_data,
        'unmet_table_data': unmet_table_data,
        'command_form_offer_add': command_form_offer_add,
        'command_form_offer_delete': command_form_offer_delete,
        'command_form_copy': command_form_copy,
        'change_log_entries': log_entries,
    })


class DayForm(forms.Form):
    day = forms.CharField(label='Day', required=True)

    def clean(self):
        cleaned_data = super(DayForm, self).clean()
        day = cleaned_data.get('day')
        if day is not None:     # day is required, but will be validated by django after this call
            try:
                DayToken.from_token(day)
            except ValueError as e:
                raise forms.ValidationError('Please input a valid day token.')
            return cleaned_data

    def get_data(self):
        return DayToken.from_token(self.cleaned_data['day'])


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


# permission: myself (as a staff), or verified center manager from the same center.
@login_required
@user_check_against_arg(
    lambda view_user_profile, target_user: view_user_profile.user == target_user or view_user_profile.is_verified() and view_user_profile.is_center_manager() and view_user_profile.is_same_center(target_user),
    lambda args, kwargs: get_object_or_404(User, pk=kwargs.get('uid')),
    lambda u: UserProfile(u)
)
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
                added_time_display = ', '.join([t.display() for t in TimeSlot.combine(added_time)])
                messages.success(request, 'Added slot(s): %s' % added_time_display)
                Log.create(Log.OFFER_UPDATE, request.user, (user_profile.user, day), 'added %s' % added_time_display)
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = SlotForm()

    form_url = reverse('slot:offer_add', kwargs={'uid': uid})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


# permission: myself only.
@login_required
@user_check_against_arg(
    lambda view_user, target_user: view_user == target_user,
    lambda args, kwargs: get_object_or_404(User, pk=kwargs.get('uid')),
)
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

            # if 'delete-all' in form.data:
            #     # deleted = OfferSlot.delete_all(day, user_profile.user)
            #     qs = OfferSlot.objects.filter(user=user, day=day)
            #     if qs.exists():
            #         qs.delete()
            #         messages.warning(request, 'Nothing to delete of the day.')
            #     else:
            #         messages.success(request, 'Delete all day is executed.')
            #         Log.create(Log.OFFER_UPDATE, request.user, (user_profile.user, day), 'deleted all day')

            # default 'submit' handler for all other submit button.
            for t in TimeToken.interval(start_time, end_time):
                # deleted = OfferSlot.delete_existing(day, user_profile.user, t)
                # if deleted:
                #     deleted_time.append(t)
                qs = OfferSlot.objects.filter(day=day, user=user_profile.user, start_time=t, end_time=t.get_next())
                if qs.exists():
                    # there should be one single offer in this queryset.
                    for offer in qs:
                        try:
                            meet = offer.meet
                            Log.create(Log.MEET_CASCADE_DELETE_OFFER, request.user, (user_profile.user, meet.need.location, day, t))
                            meet.delete()
                        except Meet.DoesNotExist:
                            pass
                        offer.delete()
                    deleted_time.append(t)

            if len(deleted_time) == 0:
                messages.warning(request, 'No available time slot is in the specified time period to delete.')
            else:
                deleted_time_display = ', '.join([t.display() for t in TimeSlot.combine(deleted_time)])
                messages.success(request, 'Deleted slot(s): %s' % deleted_time_display)
                Log.create(Log.OFFER_UPDATE, request.user, (user_profile.user, day), 'deleted %s' % deleted_time_display)

            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = SlotForm()

    form_url = reverse('slot:offer_delete', kwargs={'uid': uid})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


# check permission:
# only viewable by people from the same center. doesn't need "verified" or manager
# permission: myself (as a staff), or verified center manager from the same center.
@login_required
@user_check_against_arg(
    lambda view_user_profile, classroom: view_user_profile.is_same_center(classroom),
    lambda args, kwargs: get_object_or_404(Classroom, pk=kwargs.get('cid')),
    lambda u: UserProfile(u)
)
def day_classroom(request, cid):
    # lots of code copied from staff()
    classroom = get_object_or_404(Classroom, pk=cid)
    day = get_request_day(request)

    # check permission:
    # only viewable by people from the same center. doesn't need "verified" or manager
    # if not UserProfile(request.user).is_same_center(classroom):
    #     return defaults.permission_denied(request)

    slot_table_data = classroom.get_slot_table(day)
    unmet_table_data = classroom.get_unmet_table(day)

    # handle regular need add form
    command_form_need_add = NeedSlotForm()
    command_form_need_add.fields['day'].widget = forms.HiddenInput()
    command_form_need_add.fields['day'].initial = day.get_token()

    # handle regular need delete form
    command_form_need_delete = SlotForm()
    command_form_need_delete.fields['day'].widget = forms.HiddenInput()
    command_form_need_delete.fields['day'].initial = day.get_token()

    # copy form
    command_form_copy = DayForm()
    command_form_copy.fields['day'].widget = forms.HiddenInput()
    command_form_copy.fields['day'].initial = day.get_token()

    # assign form
    command_form_assign = AssignForm(classroom, day)
    # command_form_assign.fields['day'].widget = forms.HiddenInput()

    q = Q(ref='%d,%s' % (classroom.pk, day.get_token())) | Q(ref__contains=',%d,%s,' % (classroom.pk, day.get_token()))
    log_entries = Log.objects.filter(q, type__in=(Log.NEED_UPDATE, Log.TEMPLATE_OP_CLASSROOM, Log.MEET_UPDATE, Log.MEET_CASCADE_DELETE_OFFER)).order_by('-updated')[:20]

    return TemplateResponse(request, template='slot/classroom.html', context={
        'classroom': classroom,
        'day': day,
        'command_form_need_add': command_form_need_add,
        'command_form_need_delete': command_form_need_delete,
        'command_form_copy': command_form_copy,
        'command_form_assign': command_form_assign,
        'slot_table_data': slot_table_data,
        'unmet_table_data': unmet_table_data,
        'change_log_entries': log_entries,
    })


# permission: only verified center manager.
@login_required     # check login first, which will be executed first.
@user_is_verified
@user_is_center_manager
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
            Log.create(Log.NEED_UPDATE, request.user, (classroom, day), 'added %s' % TimeSlot(start_time.value, end_time.value).display())
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = NeedSlotForm()

    form_url = reverse('slot:need_add', kwargs={'cid': cid})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


# permission: only verified center manager.
@login_required
@user_is_verified
@user_is_center_manager
def need_delete(request, cid):
    classroom = Classroom.objects.get(pk=cid)

    if request.method == 'POST':
        form = SlotForm(request.POST)
        if form.is_valid():
            deleted_time = []
            day, start_time, end_time = form.get_cleaned_data()

            for t in TimeToken.interval(start_time, end_time):
                deleted = False
                # always delete empty needs
                qs = NeedSlot.objects.filter(location=classroom, day=day, start_time=t, end_time=t.get_next(), meet__isnull=True)
                if qs.exists():
                    qs.delete()
                    deleted = True

                if 'delete-all' in form.data:
                    # delete 'meet' as well.
                    nqs = NeedSlot.objects.filter(location=classroom, day=day, start_time=t, end_time=t.get_next())
                    if nqs.exists():
                        for need in nqs:
                            try:
                                meet = need.meet
                                Log.create(Log.MEET_CASCADE_DELETE_NEED, request.user, (meet.offer.user, need.location, need.day, need.start_time))
                                meet.delete()
                            except Meet.DoesNotExist:
                                pass
                            need.delete()
                        deleted = True

                if deleted:
                    deleted_time.append(t)

            if len(deleted_time) == 0:
                messages.warning(request, 'No available time slot is in the specified time period to delete.')
            else:
                deleted_message = ', '.join([t.display() for t in TimeSlot.combine(deleted_time)])
                messages.success(request, 'Deleted slot(s): %s' % deleted_message)
                Log.create(Log.NEED_UPDATE, request.user, (classroom, day), 'deleted %s' % deleted_message)

            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = SlotForm()

    form_url = reverse('slot:need_delete', kwargs={'cid': cid})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


@login_required
@user_is_verified
@user_is_center_manager
def assign(request, need_id):
    class AssignStaffForm(forms.Form):
        offer = forms.IntegerField(label='Assign available staff', widget=forms.Select, help_text='Every staff displayed here is available at the time slot.')

    need = get_object_or_404(NeedSlot, pk=need_id)
    # make sure start_time and end_time is right.
    assert need.start_time.get_next() == need.end_time

    # 'need' already has 'location', but we are only interested in 'classroom' for now.
    classroom = Classroom.objects.get(pk=need.location.pk)

    # check permission:
    # only viewable by people from the same center.
    if not UserProfile(request.user).is_same_center(classroom):
        return defaults.permission_denied(request)

    # try to load existing offer, or none is found.
    try:
        existing_meet = need.meet
        existing_offer = existing_meet.offer
        existing_offer_user_name = UserProfile(existing_offer.user).get_display_name()
    except Meet.DoesNotExist as e:
        existing_offer = None
        existing_offer_user_name = None

    context = {
        'need': need,
        'day': need.day,
        'time_slot': need.start_time,
        'classroom': classroom,
        'existing_offer': existing_offer,
        'existing_offer_user_name': existing_offer_user_name,
    }

    if request.method == 'POST':
        form = AssignStaffForm(request.POST)
        if 'remove' in form.data:
            Log.create(Log.MEET_UPDATE, request.user, (existing_meet.offer.user, existing_meet.need.location, need.day, need.start_time), 'removed')
            # todo: double check the logic. might need to have the 'meet' info in form as a hidden value.
            existing_meet.delete()
            messages.success(request, 'Successfully removed assignment.')
            return redirect(reverse('slot:classroom', kwargs={'cid': classroom.pk}) + '?day=' + existing_meet.offer.day.get_token())

        if form.is_valid():
            offer = OfferSlot.objects.get(pk=form.cleaned_data['offer'])
            meet = Meet(offer=offer, need=need)
            meet.save()
            messages.success(request, 'Staff assigned successfully.')
            Log.create(Log.MEET_UPDATE, request.user, (offer.user, need.location, need.day, need.start_time), 'assigned')
            return redirect(reverse('slot:classroom', kwargs={'cid': classroom.pk}) + '?day=' + offer.day.get_token())

    elif request.method == 'GET':
        form = AssignStaffForm()
    else:
        assert False

    available_offers = OfferSlot.get_available_offer(need.day, need.start_time)
    choices = [('', '- Select -')]
    choices.extend([(o.pk, UserProfile(o.user).get_display_name()) for o in available_offers])
    form.fields['offer'].widget.choices = choices

    context['form'] = form if len(choices) > 1 else None
    return render(request, 'slot/assign.html', context)


# permission: either myself of verified center manager.
@login_required
@user_check_against_arg(
    lambda view_user_profile, target_user: view_user_profile.user == target_user or view_user_profile.is_verified() and view_user_profile.is_center_manager() and view_user_profile.is_same_center(target_user),
    lambda args, kwargs: get_object_or_404(User, pk=kwargs.get('uid')),
    lambda u: UserProfile(u)
)
def staff_copy(request, uid):
    staff = UserProfile.get_by_id(uid)
    assert staff.is_center_staff()

    if request.method == 'POST':
        form = DayForm(request.POST)
        if form.is_valid():
            day = form.get_data()
            OfferSlot.copy(staff.user, day)
            messages.success(request, 'Copy template executed.')
            Log.create(Log.TEMPLATE_OP_STAFF, request.user, (staff.user, day))
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = DayForm()

    form_url = reverse('slot:staff_copy', kwargs={'uid': uid})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


@login_required
@user_is_verified
@user_is_center_manager
def classroom_copy(request, cid):
    classroom = get_object_or_404(Classroom, pk=cid)

    if request.method == 'POST':
        form = DayForm(request.POST)
        if form.is_valid():
            day = form.get_data()
            assert not day.is_regular()
            NeedSlot.copy(classroom, day)
            Meet.copy_by_location(classroom, day)
            messages.success(request, 'Copy template executed.')
            Log.create(Log.TEMPLATE_OP_CLASSROOM, request.user, (classroom, day))
            # log_need_update(request.user, classroom, day, 'deleted slot(s)')
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = DayForm()

    form_url = reverse('slot:classroom_copy', kwargs={'cid': cid})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})


class AssignForm(SlotForm):
    staff = forms.TypedChoiceField(choices=(), label='Available staff', coerce=int, required=True)

    def __init__(self, classroom, day, *args, **kwargs):
        super(AssignForm, self).__init__(*args, **kwargs)
        unmet_need_time = classroom.get_unmet_need_time(day)
        # find all staff in the center who are available at the time when the classroom has unmet need.
        list_staff = User.objects.filter(profile__centers=classroom.center, profile__verified=True, offerslot__day=day,
                            offerslot__start_time__in=unmet_need_time, offerslot__meet__isnull=True).distinct()
        self.fields['staff'].choices = [('', '- Select -')] + [(u.pk, u.get_full_name() or u.username) for u in list_staff]
        self.fields['day'].widget = forms.HiddenInput()
        self.fields['day'].initial = day.get_token()


@login_required
@user_is_verified
@user_is_center_manager
def classroom_assign(request, cid):
    classroom = get_object_or_404(Classroom, pk=cid)
    day = get_request_day(request)

    if request.method == 'POST':
        form = AssignForm(classroom, day, request.POST)
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
                    Log.create(Log.MEET_UPDATE, request.user, (offer.user, need.location, day, t), 'assigned in batch')

            if len(assigned_list) > 0:
                messages.success(request, 'Assigned slot(s): %s' % TimeSlot.display_combined(assigned_list))
            else:
                messages.warning(request, 'No assignment made due to mismatch between staff availability and classroom needs in the specified time period.')
            return redirect(request.GET.get('next', request.META['HTTP_REFERER']))

    if request.method == 'GET':
        form = AssignForm(classroom, day)

    form_url = request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else reverse('slot:classroom_assign', kwargs={'cid': cid})
    return render(request, 'base_form.html', {'form': form, 'form_url': form_url})