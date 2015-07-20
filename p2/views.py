from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect
from account.forms import LoginEmailForm
from contract.models import Contract, Engagement, Match
from s2c2.utils import dummy


def home(request):
    if request.user.is_anonymous():
        return render(request, 'landing_p2.html', {'form': LoginEmailForm()})
    else:
        # find engagement for the user
        user = request.puser
        if user.is_onboard():
            return redirect(reverse('contract:list'))
        else:
            return redirect(reverse('onboard_start'))