import json
from account.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render

# Create your views here.
from django.views.generic import FormView
from circle.forms import ManagePublicForm, ManagePersonalForm, ManageLoopForm
from circle.models import Membership, Circle
from puser.models import PUser


# class ManageCircleView(LoginRequiredMixin, FormView):
#     template_name = 'account/manage/circle.html'
#     form_class = ManagePublicForm
#     success_url = reverse_lazy('account_circle')
#
#     def get_initial(self):
#         initial = super(ManageCircleView, self).get_initial()
#         circles = Membership.objects.filter(member=self.request.user, circle__type=Circle.Type.PUBLIC.value, active=True).values_list('circle', flat=True).distinct()
#         initial['circle'] = ','.join(list(map(str, circles)))
#         return initial
#
#     def get_form_kwargs(self):
#         kwargs = super(ManageCircleView, self).get_form_kwargs()
#         kwargs['puser'] = self.request.puser
#         return kwargs
#
#     def form_valid(self, form):
#         if form.has_changed():
#             new_set = set(form.get_circle_id_list())
#             puser = form.puser
#             old_set = set(Membership.objects.filter(member=self.request.user, circle__type=Circle.Type.PUBLIC.value, active=True).values_list('circle', flat=True).distinct())
#             # unsubscribe old set not in new set
#             for circle_id in old_set - new_set:
#                 membership = Membership.objects.get(circle__id=circle_id, member=puser)
#                 membership.active = False
#                 membership.save()
#             # subscribe new set not in old set
#             for circle_id in new_set - old_set:
#                 circle = Circle.objects.get(pk=circle_id)
#                 puser.join(circle)
#             messages.success(self.request, 'Circles updated.')
#         return super(ManageCircleView, self).form_valid(form)


# obsolte in favor of ManagePersonal
# class ManageFavoriteView(LoginRequiredMixin, FormView):
#     template_name = 'account/manage/favorite.html'
#     form_class = ManagePersonalForm
#     success_url = reverse_lazy('account_favorite')
#
#     def get_old_email_qs(self):
#         return Membership.objects.filter(circle__owner=self.request.puser, circle__type=Circle.Type.PERSONAL.value, active=True).order_by('updated').values_list('member__email', flat=True).distinct()
#
#     def form_valid(self, form):
#         if form.has_changed():
#             personal_circle = self.request.puser.get_personal_circle()
#             old_set = set(self.get_old_email_qs())
#             # we get: dedup, valid email
#             new_set = set(form.get_favorite_email_list())
#
#             # remove old users from list if not exists
#             for email in old_set - new_set:
#                 target_puser = PUser.get_by_email(email)
#                 membership = personal_circle.get_membership(target_puser)
#                 if membership.active:
#                     membership.active = False
#                     membership.save()
#
#             for email in new_set - old_set:
#                 target_puser = PUser.get_or_create(email)
#                 membership = personal_circle.add_member(target_puser)
#                 if not membership.active:
#                     membership.active = True
#                     membership.save()
#
#         return super().form_valid(form)
#
#     def get_initial(self):
#         initial = super().get_initial()
#         email_qs = self.get_old_email_qs()
#         initial['favorite'] = '\n'.join(list(email_qs))
#         return initial


class ManagePersonal(LoginRequiredMixin, FormView):
    template_name = 'circle/manage_personal.html'
    form_class = ManagePersonalForm
    success_url = reverse_lazy('account_view')

    def get_old_email_qs(self):
        # return Membership.objects.filter(circle__owner=self.request.puser, circle__type=Circle.Type.PERSONAL.value, active=True).exclude(member=self.request.puser).order_by('updated').values_list('member__email', flat=True).distinct()
        # we don't exclude "myself"
        return Membership.objects.filter(circle__owner=self.request.puser, circle__type=Circle.Type.PERSONAL.value, active=True).order_by('updated').values_list('member__email', flat=True).distinct()

    def form_valid(self, form):
        if form.has_changed():
            personal_circle = self.request.puser.get_personal_circle()
            old_set = set(self.get_old_email_qs())
            # we get: dedup, valid email
            new_set = set(form.get_favorite_email_list())

            # remove old users from list if not exists
            for email in old_set - new_set:
                target_puser = PUser.get_by_email(email)
                membership = personal_circle.get_membership(target_puser)
                if membership.active:
                    membership.active = False
                    membership.save()

            for email in new_set - old_set:
                target_puser = PUser.get_or_create(email)
                personal_circle.add_member(target_puser)
                # notification for personal list change is handled in signal

            messages.success(self.request, 'Successfully updated favorite list.')

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        email_qs = self.get_old_email_qs()
        initial['favorite'] = '\n'.join(list(email_qs))
        return initial


class ManagePublic(LoginRequiredMixin, FormView):
    template_name = 'circle/manage_public.html'
    form_class = ManagePublicForm
    success_url = reverse_lazy('account_view')

    def get_initial(self):
        initial = super().get_initial()
        circles = Membership.objects.filter(member=self.request.user, circle__type=Circle.Type.PUBLIC.value, active=True).values_list('circle', flat=True).distinct()
        initial['circle'] = ','.join(list(map(str, circles)))
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
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
                # todo: not sure whether we should set approved to false.
                membership.approved = False
                membership.save()

            # subscribe new set not in old set
            for circle_id in new_set - old_set:
                circle = Circle.objects.get(pk=circle_id)
                circle.add_member(puser)
                # notification for membership approval is handled in signal

            messages.success(self.request, 'Circles updated.')
        return super().form_valid(form)


class ManageLoop(LoginRequiredMixin, FormView):
    template_name = 'circle/manage_loop.html'
    form_class = ManageLoopForm
    success_url = reverse_lazy('account_view')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['puser'] = self.request.puser
        return kwargs

    def form_valid(self, form):
        updated = False
        if form.has_changed():
            data = form.cleaned_data.get('data')
            parsed_data = json.loads(data)
            for m in parsed_data:
                try:
                    membership = Membership.objects.get(pk=m['membership_id'])
                    if membership.approved != m['approved']:
                        membership.approved = m['approved']
                        membership.save()
                        updated = True
                except Membership.DoesNotExist:
                    pass
            if updated:
                messages.success(self.request, 'Successfully updated personal circles you belong to.')
        return super().form_valid(form)