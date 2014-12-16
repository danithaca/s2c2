from django.shortcuts import render
from django.contrib.auth import views as auth_views


def signup(request):
    return render(request, 'user/signup.jinja2')


def login(request):
    return auth_views.login(request, template_name='user/login.jinja2', extra_context={'next': '/'})