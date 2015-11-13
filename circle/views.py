from itertools import groupby
import json
import re

from braces.views import LoginRequiredMixin, FormValidMessageMixin, UserPassesTestMixin, JSONResponseMixin, AjaxResponseMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse


# Create your views here.
from django.forms import HiddenInput
from django.shortcuts import redirect
from django.views.defaults import bad_request, permission_denied
from django.views.generic import FormView, CreateView, UpdateView, TemplateView, DetailView, View
from django.views.generic.detail import SingleObjectMixin
from circle.forms import UserConnectionForm, CircleCreateForm, MembershipCreateForm, MembershipEditForm
from circle.models import Membership, Circle, UserConnection
from circle.tasks import circle_send_invitation
from puser.models import PUser
from p2.utils import RegisteredRequiredMixin, UserRole, is_valid_email


################# Mixins ##################


# todo/bug: for public circles, admins can't edit "active". for personal circles, owners can't edit "approved".
class AllowMembershipEditMixin(UserPassesTestMixin):
    """
    Test if the user is able to edit the given membership. Requires implementing "get_membership".
    """
    raise_exception = True

    def test_func(self, user):
        membership = self.get_membership()
        if membership.member.id == user.id \
                or membership.circle.owner.id == user.id \
                or user.id in [member.id for member in membership.circle.members.filter(membership__as_admin=True)]:
            return True
        else:
            return False

    def get_membership(self):
        raise NotImplementedError()


class CircleAdminMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self, user):
        circle = self.get_circle()
        if user in circle.get_admin_users():
            return True
        else:
            return False

    def get_circle(self):
        return self.get_object()


################## regular views ####################


class CircleView(LoginRequiredMixin, RegisteredRequiredMixin, DetailView):
    model = Circle
    template_name = 'circle/view/base.html'
    context_object_name = 'circle'


class PersonalCircleView(CircleView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(type=Circle.Type.PERSONAL.value)

    def add_extra_filter(self, queryset):
        raise NotImplementedError()

    def get_object(self, queryset=None):
        return self.request.puser.get_personal_circle()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_personal_circle = self.object
        me = my_personal_circle.owner

        # my network
        list_membership = my_personal_circle.membership_set.filter(active=True).exclude(approved=False).exclude(member=me).order_by('-updated')
        list_membership = self.add_extra_filter(list_membership)
        context['list_membership'] = list_membership

        # my extended network
        my_parent_list = [m.member for m in my_personal_circle.membership_set.filter(active=True, approved=True, as_role=UserRole.PARENT.value).exclude(member=me)]
        extended_circle_list = Circle.objects.filter(owner__in=my_parent_list, type=my_personal_circle.type, area=my_personal_circle.area)
        # need to sort by member in order to use groupby.
        extended = []
        list_extended = Membership.objects.filter(active=True, circle__in=extended_circle_list).exclude(member=me).exclude(approved=False).exclude(member__id__in=list_membership.values_list('member__id', flat=True)).order_by('member', '-updated')
        list_extended = self.add_extra_filter(list_extended)
        for member, membership_list in groupby(list_extended, lambda m: m.member):
            extended.append(UserConnection(me, member, list(membership_list)))
        context['list_extended'] = extended

        context['full_access'] = True

        return context


class ParentManageView(PersonalCircleView):
    template_name = 'circle/view/parent.html'

    def add_extra_filter(self, queryset):
        return queryset.filter(as_role=UserRole.PARENT.value)


class SitterManageView(PersonalCircleView):
    template_name = 'circle/view/sitter.html'

    def add_extra_filter(self, queryset):
        return queryset.filter(as_role=UserRole.SITTER.value)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_sitter'] = True
        return context


# the name is similar to PersonalCircleView,
class GroupDirectoryView(LoginRequiredMixin, RegisteredRequiredMixin, TemplateView):
    template_name = 'circle/group/directory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        area = self.request.puser.get_area()
        context['area'] = area

        mapping = {m.circle: m for m in Membership.objects.filter(circle__type=Circle.Type.PUBLIC.value, member=self.request.puser, active=True, circle__area=area).exclude(approved=False)}
        context['list_circle'] = []
        for circle in Circle.objects.filter(type=Circle.Type.PUBLIC.value, area=area, active=True).order_by('-updated', '-created'):
            if circle in mapping:
                circle.user_membership = mapping[circle]
            context['list_circle'].append(circle)
        return context


class GroupCreateView(LoginRequiredMixin, RegisteredRequiredMixin, CreateView):
    model = Circle
    form_class = CircleCreateForm
    template_name = 'circle/group/add.html'
    success_url = reverse_lazy('circle:group')

    def form_valid(self, form):
        circle = form.instance
        circle.type = Circle.Type.PUBLIC.value
        circle.owner = self.request.puser
        circle.area = self.request.puser.get_area()
        result = super().form_valid(form)
        # add the user who created the new group
        circle.activate_membership(self.request.puser, as_admin=True)
        circle.approve_membership(self.request.puser)
        return result


class GroupEditView(LoginRequiredMixin, RegisteredRequiredMixin, CircleAdminMixin, UpdateView):
    model = Circle
    form_class = CircleCreateForm
    template_name = 'circle/group/add.html'
    context_object_name = 'circle'

    def get_success_url(self):
        return reverse('circle:group_view', kwargs={'pk': self.object.id})


class PublicCircleView(CircleView):
    template_name = 'circle/view/group.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(type=Circle.Type.PUBLIC.value)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        circle = self.get_object()

        # all members in the public circle
        list_membership = circle.membership_set.filter(active=True).exclude(approved=False).order_by('-updated')
        context['list_membership'] = list_membership

        try:
            context['user_membership'] = circle.get_membership(self.request.puser)
        except:
            pass

        context['full_access'] = True
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


class GroupJoinView(LoginRequiredMixin, RegisteredRequiredMixin, SingleObjectMixin, FormValidMessageMixin, FormView):
    model = Circle
    form_class = MembershipCreateForm
    context_object_name = 'circle'
    template_name = 'circle/group/join.html'
    form_valid_message = 'Successfully joined the group.'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        circle = self.object
        current_user = self.request.puser
        self.existing_membership = None
        try:
            membership = circle.get_membership(current_user)
            self.existing_membership = membership
            if membership.is_disapproved():
                messages.error(request, 'Your are not allowed to join this group. Please contact the group administrators and have them manually add you into the group.')
                return permission_denied(request)
            elif membership.active:
                messages.info(request, 'You have already joined this group. Edit your membership here.')
                return redirect(reverse('circle:membership_edit_group', kwargs={'pk': membership.id}))
        except Membership.DoesNotExist:
            pass
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        circle = self.get_object().to_proxy()
        circle.activate_membership(self.request.puser)
        note = form.cleaned_data.get('note', None)
        if form.has_changed() and note:
            membership = circle.get_membership(self.request.puser)
            membership.note = note
            membership.save()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        if self.existing_membership is not None:
            initial['instance'] = self.existing_membership

    def get_success_url(self):
        return reverse('circle:group_view', kwargs={'pk': self.get_object().id})


# todo: this has potential problem. e.g., a member goes to the personal circle and change herself as "admin".
class MembershipEditView(LoginRequiredMixin, RegisteredRequiredMixin, AllowMembershipEditMixin, UpdateView):
    model = Membership
    form_class = MembershipEditForm
    template_name = 'circle/membership_edit.html'

    def get_membership(self):
        return self.get_object()

    # def form_valid(self, form):
    #     # self.redirect_url = form.cleaned_data['redirect']
    #     return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['circle'] = self.get_membership().circle
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        membership = self.get_object()
        if membership.is_valid_parent_relation():
            form.fields['note'].label = 'Endorsement'
            form.fields['as_admin'].label = 'Mark as a family member'
        elif membership.is_valid_sitter_relation():
            form.fields['note'].label = 'Endorsement'
            form.fields['as_admin'].widget = HiddenInput()
            form.fields['as_admin'].initial = False
        elif membership.is_valid_group_membership():
            form.fields['note'].label = 'Group Affiliation'
            if self.request.puser.id in set([u.id for u in membership.circle.get_admin_users()]):
                form.fields['as_admin'].label = 'Mark as group administrator'
                # form.fields['as_admin'].help_text = 'This option available only to current administrators'
            else:
                form.fields['as_admin'].widget = HiddenInput()
        return form

    def get_success_url(self):
        membership = self.get_object()
        if membership.is_valid_parent_relation():
            return reverse('circle:parent')
        elif membership.is_valid_sitter_relation():
            return reverse('circle:sitter')
        elif membership.is_valid_group_membership():
            return reverse('circle:group_view', kwargs={'pk': membership.circle.id})
        # if self.redirect_url:
        #     return self.redirect_url
        # else:
        #     return '/'
        return '/'


class ListMembersView(LoginRequiredMixin, RegisteredRequiredMixin, TemplateView):
    template_name = 'circle/network.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_user = self.request.puser
        if target_user.is_registered():
            my_parents = list(Membership.objects.filter(circle=target_user.my_circle(Circle.Type.PARENT), active=True, approved=True).exclude(member=target_user).order_by('-updated'))
            my_sitters = list(Membership.objects.filter(circle=target_user.my_circle(Circle.Type.SITTER), active=True, approved=True).exclude(member=target_user).order_by('-updated'))
            context.update({
                'my_parents': my_parents,
                'my_sitters': my_sitters,
            })
        return context


################## views for API ########################


# note: this requires CircleAdminMixin, which is for Circle admins only
# this should not be used for regular users joining a public group, because they don't have CircleAdmin
class ActivateMembership(LoginRequiredMixin, CircleAdminMixin, SingleObjectMixin, JSONResponseMixin, AjaxResponseMixin, View):
    model = Circle

    def post_ajax(self, request, *args, **kwargs):
        circle = self.get_circle().to_proxy()
        email_field = request.POST.get('email_field', None)
        is_sitter = json.loads(request.POST.get('is_sitter', 'false'))      # this is json string.
        as_role = UserRole.PARENT.value if not is_sitter else UserRole.SITTER.value
        processed_list = []
        invalid_list = []

        if email_field:
            for email in [e.strip() for e in re.split(r'[\s,;]+', email_field)]:
                if is_valid_email(email):
                    try:
                        target_puser = PUser.get_by_email(email)
                    except PUser.DoesNotExist:
                        target_puser = PUser.create(email, dummy=True, area=circle.area)

                    # todo: here we might want to test if the membership is already active.
                    # this behaves differently for different circle type (Proxy subclass)
                    circle.activate_membership(target_puser, as_role=as_role)

                    # if this is a public circle, and since this is added by the admin, we can say that the membership is approved
                    # if this is private circle, since this is added by "email", we'll approve as well.
                    circle.approve_membership(target_puser)

                    if circle.is_membership_activated(target_puser):
                        # send notification
                        # if the user is a dummy user, send invitation code instead.
                        current_user = self.request.user.to_puser()     # this is to make a separate copy of the user to prevent "change dict" error at runtime
                        circle_send_invitation.delay(circle, target_puser, current_user)
                        processed_list.append(email)
                    else:
                        invalid_list.append(email)
                else:
                    invalid_list.append(email)

        if len(processed_list) > 0:
            messages.success(request, 'Successfully added %s' % ', '.join(processed_list))
        return self.render_json_response({'processed': processed_list, 'invalid': invalid_list})


# todo: AllowMembershipEditMixin is not very accurate
class DeactivateMembership(LoginRequiredMixin, AllowMembershipEditMixin, SingleObjectMixin, JSONResponseMixin, AjaxResponseMixin, View):
    model = Membership

    def get_membership(self):
        return self.get_object()

    def post_ajax(self, request, *args, **kwargs):
        membership = self.get_membership()
        membership.deactivate()
        # reload_membership = Membership.objects.get(id=membership.id)
        # assert reload_membership.active == False
        return self.render_json_response({'success': True})
