from django.shortcuts import render
from account.forms import LoginEmailForm
from s2c2.utils import dummy


def home(request):
    if request.user.is_anonymous():
        return render(request, 'home_p2.html', {'form': LoginEmailForm()})
    else:
        return dummy(request)