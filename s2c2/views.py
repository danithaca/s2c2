from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.template.response import TemplateResponse
from location.models import Classroom

from user.models import UserProfile


def home(request):
    # username = request.user.get_username() if request.user.is_authenticated() else str(request.user)
    # return render(request, 'home.jinja2', {'username': username})
    if request.user.is_anonymous():
        return render(request, 'home.jinja2', {'form': AuthenticationForm()})
    else:
        return redirect('dashboard')


@login_required
def dashboard(request, uid=None):
    try:
        u = User.objects.get(pk=uid)
    except User.DoesNotExist as e:
        u = request.user

    user_profile = UserProfile(u)
    context = {'user_profile': user_profile}

    if user_profile.is_center_manager():
        context.update({'header_extra': 'Manager, NCCC'})
    elif user_profile.is_center_staff():
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
