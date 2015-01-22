from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.template.response import TemplateResponse
from django.views.generic import ListView
from django.views import defaults
from django import forms

from location.models import Classroom, Center
from log.models import Notification
from s2c2.utils import get_request_day, dummy
from slot.models import DayToken
from user.models import UserProfile, CenterStaff, GroupRole


def home(request):
    # username = request.user.get_username() if request.user.is_authenticated() else str(request.user)
    # return render(request, 'home.jinja2', {'username': username})
    if request.user.is_anonymous():
        return render(request, 'home.jinja2', {'form': AuthenticationForm()})
    else:
        return redirect('dashboard')


@login_required
def dashboard(request, uid=None):
    user_profile = UserProfile.get_by_id_default(uid, request.user)
    current_user_profile = UserProfile(request.user)

    # check permission:
    # we only allow view different user's profile if the viewing user is verified and belongs to the same center as the viewed user.
    if user_profile != current_user_profile and (not current_user_profile.is_verified() or not user_profile.is_same_center(current_user_profile)):
        return defaults.permission_denied(request)

    day = get_request_day(request)

    context = {
        'user_profile': user_profile,
        'day': day,
    }

    if user_profile.is_center_staff():
        context['week_table_data'] = user_profile.get_week_table(day)
        context['week_hours'] = user_profile.get_week_hours(day)

    if user_profile != current_user_profile and current_user_profile.is_center_manager() \
            and current_user_profile.is_verified() and not user_profile.is_verified() \
            and current_user_profile.is_same_center(user_profile):
        # then we allow verify form
        # this form is similar to user:verify()::VerifyForm, but we use IntegerField instead.
        # note that user:verify()::VerifyForm will validate the data using MultipleChoicesField.
        class VerifyForm(forms.Form):
            users = forms.IntegerField(widget=forms.HiddenInput, initial=user_profile.pk)
        context['verify_form'] = VerifyForm()

    return TemplateResponse(request, template='dashboard.jinja2', context=context)


@login_required
def classroom_home(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    day = get_request_day(request)

    # check permission:
    # only viewable by people from the same center. doesn't need "verified".
    if not UserProfile(request.user).is_same_center(classroom):
        return defaults.permission_denied(request)

    classroom_staff = classroom.get_staff()
    week_table_data = classroom.get_week_table(day)

    return TemplateResponse(request, template='classroom.jinja2', context={
        'classroom': classroom,
        'day': day,
        'classroom_staff': classroom_staff,
        'week_table_data': week_table_data,
        'week_unmet_need_warning': classroom.exists_unmet_need(day),
    })


@login_required
def notification(request):

    class NotificationView(ListView):
        template_name = 'notification.jinja2'
        context_object_name = 'latest_notification'
        # see http://stackoverflow.com/questions/11494483/django-class-based-view-how-do-i-pass-additional-parameters-to-the-as-view-meth
        user = None

        def get_queryset(self):
            return Notification.objects.filter(receiver=self.user)

    return NotificationView.as_view(user=request.user)(request)


@login_required
def center_home(request, pk, tab='directory'):
    center = get_object_or_404(Center, pk=pk)

    # check permission:
    # only viewable by people from the same center. doesn't need "verified".
    if not UserProfile(request.user).is_same_center(center):
        return defaults.permission_denied(request)

    context = {'center': center, 'tab': tab, }
    list_classroom = Classroom.objects.filter(center=center)

    manager_group = GroupRole.get_by_name('manager')
    teacher_group = GroupRole.get_by_name('teacher')
    support_group = GroupRole.get_by_name('support')
    intern_group = GroupRole.get_by_name('intern')
    managers = User.objects.filter(profile__centers=center, groups=manager_group.group, is_active=True)
    context['managers'] = managers

    # handle directory tab
    if tab == 'directory':

        sections = (
            (teacher_group.name, User.objects.filter(profile__centers=center, groups=teacher_group.group, is_active=True)),
            (support_group.name, User.objects.filter(profile__centers=center, groups=support_group.group, is_active=True)),
            (intern_group.name, User.objects.filter(profile__centers=center, groups=intern_group.group, is_active=True)),
        )
        context.update({'classrooms': list_classroom, 'sections': sections})

    # handle list of classroom tab
    elif tab == 'list-classroom':
        context['list_classroom'] = list_classroom
        day = get_request_day(request)
        context['day'] = day

    # handle list of staff tab.
    elif tab == 'list-staff':
        list_staff = [CenterStaff(u) for u in User.objects.filter(profile__centers=center, groups__in=[teacher_group.group, support_group.group, intern_group.group], is_active=True)]
        context['list_staff'] = list_staff

    else:
        assert False

    return render(request, 'center.jinja2', context)
