from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from s2c2.utils import dummy


def home(request):
    if request.user.is_anonymous():
        return render(request, 'home_p2.html', {'form': AuthenticationForm()})
    else:
        return dummy(request)