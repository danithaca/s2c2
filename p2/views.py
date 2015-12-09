from collections import defaultdict

from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from account.forms import LoginEmailForm
from django.views.generic import TemplateView
from circle.models import Membership, Circle
from contract.models import Contract

from puser.forms import WaitingForm


def home(request):
    if request.user.is_anonymous():
        return redirect(reverse('about'))
    else:
        puser = request.puser
        if not puser.is_registered():
            return redirect('account_signup')
        else:
            return redirect('contract:engagement_list')


class HelpView(TemplateView):
    template_name = 'pages/help.html'


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class TourView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/tour.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_user = self.request.puser
        context['current_user'] = target_user
        if target_user.is_registered():
            my_parents = list(Membership.objects.filter(circle=target_user.my_circle(Circle.Type.PARENT), active=True, approved=True).exclude(member=target_user).order_by('-updated'))
            my_memberships = list(Membership.objects.filter(member=target_user, circle__type=Circle.Type.TAG.value, circle__area=target_user.get_area(), active=True))
            context['my_parents'] = my_parents
            context['my_memberships'] = my_memberships
        return context


class SitemapView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/sitemap.html'


class ExperimentView(TemplateView):
    template_name = 'pages/experiment.html'


class ErrorView(TemplateView):
    template_name = '404.html'


class LogoView(TemplateView):
    template_name = 'pages/logo.html'


class LandingView(TemplateView):
    template_name = 'pages/landing.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_login'] = LoginEmailForm()
        ctx['form_signup'] = WaitingForm()
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