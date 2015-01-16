from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.template.response import TemplateResponse
from django.views.generic import ListView

from location.models import Classroom, Center
from log.models import Notification
from slot.models import DayToken
from user.models import UserProfile, CenterStaff


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
    context = {
        'user_profile': user_profile,
        'day': DayToken.today(),
    }

    if user_profile.is_center_manager():
        context.update({'header_extra': 'Manager, NCCC'})
    elif user_profile.is_center_staff():
        context['regular_week_table_data'] = user_profile.get_regular_week_table()
        context.update({'header_extra': 'Staff, NCCC'})
    else:
        context.update({'header_extra': ''})

    return TemplateResponse(request, template='dashboard.jinja2', context=context)


@login_required
def classroom(request, pk):
    cr = get_object_or_404(Classroom, pk=pk)
    return TemplateResponse(request, template='classroom.jinja2', context={
        'classroom': cr
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
def center(request, pk):
    center = get_object_or_404(Center, pk=pk)
    return render(request, 'center.jinja2', {
        'center': center,
    })