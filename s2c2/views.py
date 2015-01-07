from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm


def home(request):
    # username = request.user.get_username() if request.user.is_authenticated() else str(request.user)
    # return render(request, 'home.jinja2', {'username': username})
    return render(request, 'home.jinja2', {'form': AuthenticationForm()})