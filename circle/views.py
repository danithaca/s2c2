from itertools import groupby
import json

from account.mixins import LoginRequiredMixin
from braces.views import FormValidMessageMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse


# Create your views here.
from django.views.defaults import bad_request
from django.views.generic import FormView
from circle.forms import ManagePublicForm, ManagePersonalForm, ManageLoopForm, ManageAgencyForm, EmailListForm, \
    UserConnectionForm
from circle.models import Membership, Circle, ParentCircle, UserConnection
from circle.tasks import personal_circle_send_invitation, circle_send_invitation
from puser.models import PUser
from p2.utils import UserOnboardRequiredMixin, ControlledFormValidMessageMixin


class BaseCircleView(LoginRequiredMixin, UserOnboardRequiredMixin, ControlledFormValidMessageMixin, FormView):
    form_class = EmailListForm
    default_approved = None

    def get_old_email_qs(self):
        circle = self.get_circle()
        return Membership.objects.filter(circle=circle, active=True).exclude(member=self.request.puser).order_by('updated').values_list('member__email', flat=True).distinct()

    def form_valid(self, form):
        if form.has_changed() or form.cleaned_data.get('force_save', False):
            circle = self.get_circle()
            old_set = set(self.get_old_email_qs())
            # we get: dedup, valid email
            new_set = set(form.get_favorite_email_list())

            # remove old users from list if not exists
            for email in old_set - new_set:
                self.show_message = True
                target_puser = PUser.get_by_email(email)
                circle.deactivate_membership(target_puser)

            # add new user
            for email in new_set - old_set:
                self.show_message = True
                try:
                    target_puser = PUser.get_by_email(email)
                except PUser.DoesNotExist:
                    target_puser = PUser.create(email, dummy=True, area=circle.area)
                # this behaves differently for different circle type (Proxy subclass)
                circle.activate_membership(target_puser, approved=self.default_approved)
                if form.cleaned_data.get('send', False):
                    # send notification
                    # if the user is a dummy user, send invitation code instead.
                    circle_send_invitation.delay(circle, target_puser)

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        email_qs = self.get_old_email_qs()
        initial['favorite'] = '\n'.join(list(email_qs))
        return initial


class ParentCircleView(BaseCircleView):
    template_name = 'circle/parent.html'
    success_url = reverse_lazy('circle:parent')
    form_valid_message = 'Parent connections successfully updated.'
    # we always set "approved" to be true here.
    default_approved = True

    def get_circle(self):
        circle = self.request.puser.my_circle(Circle.Type.PARENT)
        assert isinstance(circle, ParentCircle)
        return circle


class SitterCircleView(BaseCircleView):
    template_name = 'circle/sitter.html'
    success_url = reverse_lazy('circle:sitter')
    form_valid_message = 'Successfully updated your paid babysitter connections.'
    # we always set "approved" to be true here.
    default_approved = True

    def get_circle(self):
        circle = self.request.puser.my_circle(Circle.Type.SITTER)
        return circle

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # find babysitter pool
        me = self.request.puser
        my_parent_circle = me.my_circle(Circle.Type.PARENT)
        my_parent_list = my_parent_circle.members.filter(membership__active=True, membership__approved=True).exclude(membership__member=me)
        other_parent_sitter_circle_list = Circle.objects.filter(owner__in=my_parent_list, type=Circle.Type.SITTER.value, area=my_parent_circle.area)
        # need to sort by member in order to use groupby.
        sitter_membership_pool = Membership.objects.filter(active=True, approved=True, circle__in=other_parent_sitter_circle_list).exclude(member=me).order_by('member')
        pool_list = []
        for member, membership_list in groupby(sitter_membership_pool, lambda m: m.member):
            pool_list.append(UserConnection(me, member, list(membership_list)))
        context['pool_list'] = pool_list
        return context


class UserConnectionView(LoginRequiredMixin, FormValidMessageMixin, FormView):
    template_name = 'pages/basic_form.html'
    form_class = UserConnectionForm
    form_valid_message = 'Updated successfully.'

    def dispatch(self, request, *args, **kwargs):
        self.initiate_user = request.puser
        self.target_user = None
        try:
            self.target_user = PUser.objects.get(pk=kwargs.get('uid', None))
        except:
            pass

        if request.method.lower() == 'get' and self.target_user is None:
            return bad_request(request)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initiate_user'] = self.initiate_user
        kwargs['target_user'] = self.target_user
        return kwargs

    # def get_initial(self):
    #     initial = super().get_initial()
    #     # this is area aware.
    #     area = self.initiate_user.get_area()
    #     initial['parent_circle'] = Membership.objects.filter(member=self.target_user, circle__owner=self.initiate_user, circle__type=Circle.Type.PARENT.value, circle__area=area, active=True, approved=True).exists()
    #     initial['sitter_circle'] = Membership.objects.filter(member=self.target_user, circle__owner=self.initiate_user, circle__type=Circle.Type.SITTER.value, circle__area=area, active=True, approved=True).exists()
    #     return initial

    def form_valid(self, form):
        for field_name, circle_type in (('parent_circle', Circle.Type.PARENT), ('sitter_circle', Circle.Type.SITTER)):
            my_circle = self.initiate_user.my_circle(circle_type)
            new_value = form.cleaned_data[field_name]
            old_value = form.initial[field_name]
            if new_value != old_value:
                if new_value:
                    # todo: here we just approve.
                    my_circle.activate_membership(self.target_user, approved=True)
                else:
                    my_circle.deactivate_membership(self.target_user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('account_view', kwargs={'pk': self.target_user.id})