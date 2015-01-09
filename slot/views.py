from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django import forms
from user.models import UserProfile
from .models import RegularSlot, DayOfWeek, HalfHourTime, OfferRegular
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

    return TemplateResponse(request, template='slot/staff_regular.jinja2', context={
        'user_profile': user_profile,
        'dow': dow,
    })


class SlotForm(forms.Form):
    start_time = forms.TypedChoiceField(choices=HalfHourTime.get_choices(time(hour=7), time(hour=19, minute=30)),
                                        required=True, coerce=HalfHourTime.parse, label='Start')
    end_time = forms.TypedChoiceField(choices=HalfHourTime.get_choices(time(hour=7, minute=30), time(hour=20)),
                                      required=True, coerce=HalfHourTime.parse, label='End')

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
            OfferRegular.add(start_time=form.cleaned_data['start_time'], end_time=form.cleaned_data['end_time'],
                             start_dow=form.cleaned_data['start_dow'], user=user_profile.user)

    if request.method == 'GET':
        form = RegularSlotForm()

    form_url = reverse('slot:offer_regular_add', kwargs={'uid': uid})
    return render(request, 'base_form.jinja2', {'form': form, 'form_url': form_url, 'uid': uid})