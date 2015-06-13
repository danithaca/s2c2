from account.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render

# Create your views here.
from django.views.generic import FormView
from circle.forms import ManageCircleForm, ManageFavoriteForm
from circle.models import Membership, Circle
from puser.models import PUser


class ManageCircleView(LoginRequiredMixin, FormView):
    template_name = 'account/manage/circle.html'
    form_class = ManageCircleForm
    success_url = reverse_lazy('account_circle')

    def get_initial(self):
        initial = super(ManageCircleView, self).get_initial()
        circles = Membership.objects.filter(member=self.request.user, circle__type=Circle.Type.PUBLIC.value, active=True).values_list('circle', flat=True).distinct()
        initial['circle'] = ','.join(list(map(str, circles)))
        return initial

    def get_form_kwargs(self):
        kwargs = super(ManageCircleView, self).get_form_kwargs()
        kwargs['puser'] = self.request.puser
        return kwargs

    def form_valid(self, form):
        if form.has_changed():
            new_set = set(form.get_circle_id_list())
            puser = form.puser
            old_set = set(Membership.objects.filter(member=self.request.user, circle__type=Circle.Type.PUBLIC.value, active=True).values_list('circle', flat=True).distinct())
            # unsubscribe old set not in new set
            for circle_id in old_set - new_set:
                membership = Membership.objects.get(circle__id=circle_id, member=puser)
                membership.active = False
                membership.save()
            # subscribe new set not in old set
            for circle_id in new_set - old_set:
                circle = Circle.objects.get(pk=circle_id)
                puser.join(circle)
            messages.success(self.request, 'Circles updated.')
        return super(ManageCircleView, self).form_valid(form)


class ManageFavoriteView(LoginRequiredMixin, FormView):
    template_name = 'account/manage/favorite.html'
    form_class = ManageFavoriteForm
    success_url = reverse_lazy('account_favorite')

    def form_valid(self, form):
        if form.has_changed():

            # we get: dedup, valid email
            email_list = form.get_favorite_email_list()
            for email in email_list:
                # 1: make sure we have the user
                pass
                # 2: remove old users from list if not exists

                # 3; add new users not in old list.
        return super(ManageFavoriteView, self).form_valid(form)
