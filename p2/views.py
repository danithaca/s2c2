from django.db.models import Q
from django.shortcuts import render
from account.forms import LoginEmailForm
from contract.models import Contract, Engagement, Match
from s2c2.utils import dummy


def home(request):
    if request.user.is_anonymous():
        return render(request, 'landing_p2.html', {'form': LoginEmailForm()})
    else:
        # find engagement for the user
        user = request.puser
        list_engagement = []
        for contract in Contract.objects.filter(Q(initiate_user=user) | Q(match__target_user=user)).distinct().order_by('-event_start'):
            if contract.initiate_user == user:
                list_engagement.append(Engagement.from_contract(contract))
            else:
                match = Match.objects.get(contract=contract, target_user=user)
                list_engagement.append(Engagement.from_match(match))

        return render(request, 'home_p2.html', {
            'user': request.puser,
            'engagements': list_engagement,
        })