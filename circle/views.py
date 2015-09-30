import json

from account.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy


# Create your views here.
from django.views.generic import FormView
from circle.forms import ManagePublicForm, ManagePersonalForm, ManageLoopForm, ManageAgencyForm
from circle.models import Membership, Circle
from circle.tasks import personal_circle_send_invitation
from puser.models import PUser
from p2.utils import UserOnboardRequiredMixin


class ParentCircleView(LoginRequiredMixin, UserOnboardRequiredMixin, FormView):
    template_name = 'circle/manage_member.html'
    form_class = ManagePersonalForm
    success_url = reverse_lazy('account_view')

    def get_old_email_qs(self):
        # return Membership.objects.filter(circle__owner=self.request.puser, circle__type=Circle.Type.PERSONAL.value, active=True).exclude(member=self.request.puser).order_by('updated').values_list('member__email', flat=True).distinct()
        # we don't exclude "myself"
        puser = self.request.puser
        my_personal_circle = puser.get_personal_circle()
        return Membership.objects.filter(circle=my_personal_circle, active=True).order_by('updated').values_list('member__email', flat=True).distinct()

    def form_valid(self, form):
        if form.has_changed() or form.cleaned_data.get('force_save', False):
            personal_circle = self.request.puser.get_personal_circle()
            old_set = set(self.get_old_email_qs())
            # we get: dedup, valid email
            new_set = set(form.get_favorite_email_list())
            updated = False

            # remove old users from list if not exists
            for email in old_set - new_set:
                updated = True
                target_puser = PUser.get_by_email(email)
                membership = personal_circle.get_membership(target_puser)
                if membership.active:
                    membership.active = False
                    membership.save()

            for email in new_set - old_set:
                updated = True
                try:
                    target_puser = PUser.get_by_email(email)
                except PUser.DoesNotExist:
                    target_puser = PUser.create(email, dummy=True, area=personal_circle.area)
                personal_circle.add_member(target_puser)
                if form.cleaned_data.get('send', False):
                    # send notification
                    # if the user is a dummy user, send invitation code instead.
                    personal_circle_send_invitation.delay(personal_circle, target_puser)

            if updated:
                messages.success(self.request, 'Successfully updated your personal favorite list.')

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        email_qs = self.get_old_email_qs()
        initial['favorite'] = '\n'.join(list(email_qs))
        return initial


class ManagePersonal(LoginRequiredMixin, UserOnboardRequiredMixin, FormView):
    template_name = 'circle/manage_personal.html'
    form_class = ManagePersonalForm
    success_url = reverse_lazy('account_view')

    def get_old_email_qs(self):
        # return Membership.objects.filter(circle__owner=self.request.puser, circle__type=Circle.Type.PERSONAL.value, active=True).exclude(member=self.request.puser).order_by('updated').values_list('member__email', flat=True).distinct()
        # we don't exclude "myself"
        puser = self.request.puser
        my_personal_circle = puser.get_personal_circle()
        return Membership.objects.filter(circle=my_personal_circle, active=True).order_by('updated').values_list('member__email', flat=True).distinct()

    def form_valid(self, form):
        if form.has_changed() or form.cleaned_data.get('force_save', False):
            personal_circle = self.request.puser.get_personal_circle()
            old_set = set(self.get_old_email_qs())
            # we get: dedup, valid email
            new_set = set(form.get_favorite_email_list())
            updated = False

            # remove old users from list if not exists
            for email in old_set - new_set:
                updated = True
                target_puser = PUser.get_by_email(email)
                membership = personal_circle.get_membership(target_puser)
                if membership.active:
                    membership.active = False
                    membership.save()

            for email in new_set - old_set:
                updated = True
                try:
                    target_puser = PUser.get_by_email(email)
                except PUser.DoesNotExist:
                    target_puser = PUser.create(email, dummy=True, area=personal_circle.area)
                personal_circle.add_member(target_puser)
                if form.cleaned_data.get('send', False):
                    # send notification
                    # if the user is a dummy user, send invitation code instead.
                    personal_circle_send_invitation.delay(personal_circle, target_puser)

            if updated:
                messages.success(self.request, 'Successfully updated your personal favorite list.')

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        email_qs = self.get_old_email_qs()
        initial['favorite'] = '\n'.join(list(email_qs))
        return initial


# be careful: UserOnboardRequired might loop back to the begining in "OnboardProcess".
class ManagePublic(LoginRequiredMixin, UserOnboardRequiredMixin, FormView):
    template_name = 'circle/manage_public.html'
    form_class = ManagePublicForm
    success_url = reverse_lazy('account_view')
    success_message = 'Circles updated.'

    def get_membership_circle_id_list(self):
        return Membership.objects.filter(member=self.request.user, circle__type=Circle.Type.PUBLIC.value, active=True, circle__area=self.request.puser.get_area()).values_list('circle', flat=True).distinct()

    def create_membership(self, circle, puser):
        circle.add_member(puser)

    # def get_initial(self):
    #     initial = super().get_initial()
    #     circles = self.get_membership_circle_id_list()
    #     initial['circle'] = ','.join(list(map(str, circles)))
    #     return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['puser'] = self.request.puser
        kwargs['membership_circle_id_list'] = self.get_membership_circle_id_list()
        return kwargs

    def form_valid(self, form):
        if form.has_changed():
            new_set = set(form.get_circle_id_list())
            puser = form.puser
            old_set = set(self.get_membership_circle_id_list())

            # unsubscribe old set not in new set
            for circle_id in old_set - new_set:
                membership = Membership.objects.get(circle__id=circle_id, member=puser)
                membership.active = False
                # membership.approved = False       # don't touch the "approved" field
                membership.save()

            # subscribe new set not in old set
            for circle_id in new_set - old_set:
                circle = Circle.objects.get(pk=circle_id)
                self.create_membership(circle, puser)
                # notification for membership approval is handled in signal

            messages.success(self.request, self.success_message)
        return super().form_valid(form)


class ManageAgency(ManagePublic):
    template_name = 'circle/manage_agency.html'
    form_class = ManageAgencyForm
    success_url = reverse_lazy('account_view')
    success_message = 'Updated agency subscriptions.'

    def get_membership_circle_id_list(self):
        return Membership.objects.filter(member=self.request.user, circle__type=Circle.Type.AGENCY.value, active=True, circle__area=self.request.puser.get_area()).values_list('circle', flat=True).distinct()

    def create_membership(self, circle, puser):
        try:
            # if membership already exists, set it to active without touching "type" or "approved".
            membership = circle.get_membership(puser)
            if not membership.active:
                membership.active = True
                membership.save()
        except Membership.DoesNotExist:
            circle.add_member(puser, membership_type=Membership.Type.PARTIAL.value, approved=True)


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
                messages.success(self.request, 'Successfully updated.')
        return super().form_valid(form)