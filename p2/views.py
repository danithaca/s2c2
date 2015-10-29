from collections import defaultdict

from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from account.forms import LoginEmailForm
from django.views.generic import TemplateView
from contract.models import Contract

from puser.forms import SignupBasicForm


def home(request):
    if request.user.is_anonymous():
        # return redirect(reverse('account_signup'))
        return redirect(reverse('about'))
    else:
        # find engagement for the user
        puser = request.puser
        if not puser.is_onboard():
            return redirect(reverse('tour'))
        # elif puser.engagement_queryset().exists():
        #     return redirect(reverse('contract:engagement_list'))
        # else:
        #     return redirect(reverse('contract:add'))
        else:
            return redirect(reverse('dashboard'))


class HelpView(TemplateView):
    template_name = 'pages/help.html'


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class TourView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/tour.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.puser
        return context


class SitemapView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/sitemap.html'


class ExperimentView(TemplateView):
    template_name = 'pages/experiment.html'


class LogoView(TemplateView):
    template_name = 'pages/logo.html'


class LandingView(TemplateView):
    template_name = 'pages/landing.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_login'] = LoginEmailForm()
        ctx['form_signup'] = SignupBasicForm()
        return ctx


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        puser = self.request.puser

        ctx['target_user'] = puser
        headline = puser.engagement_headline()
        if headline:
            ctx['engagement_headline'] = headline

        # engagement list
        display_limit = 5
        engagement_list = sorted(puser.engagement_list(lambda qs: qs.filter(initiate_user=puser).order_by('-updated')[:display_limit]) + puser.engagement_list(lambda qs: qs.filter(match__target_user=puser).order_by('-match__updated')[:display_limit]), key=lambda e: e.updated(), reverse=True)
        ctx['engagement_recent'] = engagement_list[:display_limit]

        # TODO: this is potential performance concern. use cache
        # interactions
        interactions_list = puser.engagement_list(lambda qs: qs.filter(initiate_user=puser, status=Contract.Status.SUCCESSFUL.value)) + puser.engagement_list(lambda qs: qs.filter(confirmed_match__target_user=puser, status=Contract.Status.SUCCESSFUL.value))
        interactions = defaultdict(int)
        for engagement in interactions_list:
            target_user = engagement.passive_user()
            assert target_user is not None and target_user != puser
            interactions[target_user] += 1
        ctx['interactions'] = interactions.items()

        # # favors karma
        # karma = defaultdict(int)
        # for favor in puser.engagement_favors():
        #     direction = 0
        #     if favor.is_main_contract():
        #         direction = -1
        #     elif favor.is_match_confirmed():
        #         direction = 1
        #     u = favor.passive_user()
        #     assert u is not None, 'Contract has problem: %d' % favor.contract.id
        #     karma[u] += direction
        # ctx['favors_karma'] = [(u, f) for u, f in karma.items() if f != 0]

        # # feedback needed
        # ctx['contract_feedback_needed_qs'] = puser.contract_feedback_needed_queryset()

        return ctx