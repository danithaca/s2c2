import random
from itertools import groupby
import json
import re

from braces.views import LoginRequiredMixin, FormValidMessageMixin, UserPassesTestMixin, JSONResponseMixin, AjaxResponseMixin
from django.contrib import messages
from django.core.urlresolvers import reverse

from django.forms import HiddenInput
from django.shortcuts import redirect
from django.views.defaults import permission_denied
from django.views.generic import FormView, CreateView, UpdateView, TemplateView, DetailView, View
from django.views.generic.detail import SingleObjectMixin
from circle.forms import CircleCreateForm, MembershipCreateForm, MembershipEditForm, ParentAddForm, SitterAddForm
from circle.models import Membership, Circle, UserConnection, Friendship
from circle.tasks import circle_invite
from puser.models import PUser
from p2.utils import RegisteredRequiredMixin, UserRole, is_valid_email, ObjectAccessMixin, TrustLevel
from shout.tasks import notify_send


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
        assert circle is not None
        if user in circle.get_admin_users():
            return True
        else:
            return False

    def get_circle(self):
        return self.get_object()


class CircleAccessMixin(ObjectAccessMixin):
    object_class = Circle
    trust_level = TrustLevel.NONE.value


################## regular views ####################


class CircleView(LoginRequiredMixin, RegisteredRequiredMixin, CircleAccessMixin, DetailView):
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pending_approve_membership = Membership.objects.filter(member=self.object.owner, type=Circle.Type.PERSONAL.value, approved__isnull=True, circle__type=Circle.Type.PERSONAL.value, circle__area=self.object.area)
        context['pending_membership'] = pending_approve_membership
        return context


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
    # success_url = reverse_lazy('circle:discover')

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
        list_membership = circle.membership_set.filter(active=True, as_role=UserRole.PARENT.value).exclude(approved=False).order_by('-updated')
        context['list_membership'] = list_membership
        list_sitter_membership = circle.membership_set.filter(active=True, as_role=UserRole.SITTER.value).exclude(approved=False).order_by('-updated')
        context['list_sitter_membership'] = list_sitter_membership

        context['show_sitter_switch'] = True
        try:
            user_membership = circle.get_membership(self.request.puser)
            context['user_membership'] = user_membership
        except:
            pass

        context['signup_code'] = circle.get_signup_code()
        return context


# class UserConnectionView(LoginRequiredMixin, FormValidMessageMixin, FormView):
#     template_name = 'pages/basic_form.html'
#     form_class = UserConnectionForm
#     form_valid_message = 'Updated successfully.'
#
#     def dispatch(self, request, *args, **kwargs):
#         self.initiate_user = request.puser
#         self.target_user = None
#         try:
#             self.target_user = PUser.objects.get(pk=kwargs.get('uid', None))
#         except:
#             pass
#
#         if request.method.lower() == 'get' and self.target_user is None:
#             return bad_request(request)
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['initiate_user'] = self.initiate_user
#         kwargs['target_user'] = self.target_user
#         return kwargs
#
#     # def get_initial(self):
#     #     initial = super().get_initial()
#     #     # this is area aware.
#     #     area = self.initiate_user.get_area()
#     #     initial['parent_circle'] = Membership.objects.filter(member=self.target_user, circle__owner=self.initiate_user, circle__type=Circle.Type.PARENT.value, circle__area=area, active=True, approved=True).exists()
#     #     initial['sitter_circle'] = Membership.objects.filter(member=self.target_user, circle__owner=self.initiate_user, circle__type=Circle.Type.SITTER.value, circle__area=area, active=True, approved=True).exists()
#     #     return initial
#
#     def form_valid(self, form):
#         for field_name, circle_type in (('parent_circle', Circle.Type.PARENT), ('sitter_circle', Circle.Type.SITTER)):
#             my_circle = self.initiate_user.my_circle(circle_type)
#             new_value = form.cleaned_data[field_name]
#             old_value = form.initial[field_name]
#             if new_value != old_value:
#                 if new_value:
#                     # todo: here we just approve.
#                     my_circle.activate_membership(self.target_user, approved=True)
#                 else:
#                     my_circle.deactivate_membership(self.target_user)
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse('account_view', kwargs={'pk': self.target_user.id})


# For public circle, the member is current_user, the circle is the group.
# For personal circle, the member is the target_user, the circle is the current user's personal circle. "Friendship" is symmetric, which requires permission from the target user to add the current user as well.
class CircleJoinView(LoginRequiredMixin, RegisteredRequiredMixin, SingleObjectMixin, FormValidMessageMixin, FormView):
    model = Circle
    form_class = MembershipCreateForm
    context_object_name = 'circle'

    # specifies which user is to be added to the circle.
    def get_user(self):
        return self.request.puser

    def dispatch_init(self):
        self.object = self.get_object()
        circle = self.object
        target_user = self.get_user()
        self.existing_membership = None
        # todo: check and make sure the to-be-added user (to personal circle) is not one's self.
        try:
            membership = circle.get_membership(target_user)
            self.existing_membership = membership
        except Membership.DoesNotExist:
            pass

    def send_notification(self, member, circle, introduce):
        # member is added to circle. send notification
        pass

    def extra_process(self, membership):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = self.get_user()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.existing_membership is not None:
            kwargs['instance'] = self.existing_membership
        return kwargs


class PersonalJoinView(CircleJoinView):
    form_valid_message = 'Successfully submitted your request. '

    def dispatch(self, request, *args, **kwargs):
        self.dispatch_init()
        membership = self.existing_membership
        if membership:
            assert membership.is_valid_parent_relation() or membership.is_valid_sitter_relation()
            if membership.is_disapproved():
                messages.error(request, 'You are not allowed to add this person because it is blocked.')
                return permission_denied(request)
            elif membership.active:
                msg = ''
                redirect_url = '/'
                if membership.is_valid_parent_relation():
                    msg = 'The parent is already in your network. Edit the connection here.'
                    redirect_url = reverse('circle:membership_edit', kwargs={'pk': membership.id})
                elif membership.is_valid_sitter_relation():
                    msg = 'The sitter is already in your network. Edit the connection here.'
                    redirect_url = reverse('circle:membership_edit', kwargs={'pk': membership.id})
                messages.info(request, msg)
                return redirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(type=Circle.Type.PERSONAL.value)

    def get_object(self, queryset=None):
        return self.request.puser.get_personal_circle()

    def get_user(self):
        return PUser.objects.get(pk=self.kwargs['uid'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['target_user'] = self.get_user()
        return kwargs

    def get_success_url(self):
        return reverse('account_view', kwargs={'pk': self.get_user().pk})


class ParentJoinView(PersonalJoinView):
    template_name = 'circle/membership/parent_add.html'
    form_class = ParentAddForm

    def form_valid(self, form):
        circle = self.get_object().to_proxy()
        target_user = self.get_user()
        circle.activate_membership(target_user)
        private_note = form.cleaned_data.get('private_note', None)
        as_rel = form.cleaned_data.get('as_rel', '')

        # save regardless of whether it's changed or not.
        membership = circle.get_membership(target_user)
        membership.private_note = private_note
        membership.as_rel = as_rel
        if form.cleaned_data.get('is_sitter', False):
            membership.as_role = UserRole.SITTER.value
        else:
            membership.as_role = UserRole.PARENT.value
        membership.save()

        introduce = form.cleaned_data.get('introduce', False)
        self.send_notification(target_user, circle, introduce)

        self.extra_process(membership)

        # this is not ModelView, and therefore membershihp is not automatically saved.
        return super().form_valid(form)

    def send_notification(self, member, circle, introduce):
        # will need to send a notification to "member" because circle.owner is requesting.
        ctx = {
            'circle': circle,
            'member': member,
        }
        if introduce:
            uc = UserConnection(circle.owner, member)
            shared_connection = uc.find_shared_connection_personal_symmetric()
            cc_list = shared_connection
            ctx['shared_connection'] = shared_connection
        else:
            cc_list = []
        notify_send.delay(circle.owner, member, 'circle/messages/added_parent', ctx=ctx, cc_user_list=cc_list)

    def extra_process(self, membership):
        super().extra_process(membership)
        # mark "as_rel" of friendship membership
        # at this point, the "reverse membership" should already been created.
        friendship = Friendship(membership.circle.owner, membership.member, membership)
        reverse_membership = friendship.reverse_membership
        assert reverse_membership is not None
        reverse_membership.as_rel = membership.as_rel
        reverse_membership.save()


class SitterJoinView(PersonalJoinView):
    template_name = 'circle/membership/sitter_add.html'
    form_class = SitterAddForm

    def form_valid(self, form):
        circle = self.get_object().to_proxy()
        target_user = self.get_user()
        circle.activate_membership(target_user, as_role=UserRole.SITTER.value)
        private_note = form.cleaned_data.get('private_note', None)

        # save regardless of whether it's changed or not.
        membership = circle.get_membership(target_user)
        membership.private_note = private_note
        membership.as_role = UserRole.SITTER.value
        introduce = form.cleaned_data.get('introduce', False)
        if introduce:
            # here, we implicitly infer that if "asking for introduction" means that there's no strength.
            membership.strength = 0.0
        membership.save()

        # send notification.
        self.send_notification(target_user, circle, introduce)

        # auto approve this membership
        # todo: think about whether to auto approve sitter_add
        circle.approve_membership(membership.member)

        # this is not ModelView, and therefore membershihp is not automatically saved.
        return super().form_valid(form)

    def send_notification(self, member, circle, introduce):
        # will need to send a notification to "member" because circle.owner is requesting.
        ctx = {
            'circle': circle,
            'member': member,
        }
        if introduce:
            uc = UserConnection(circle.owner, member)
            shared_connection = set([m.circle.owner for m in uc.find_shared_connection_personal()])
            cc_list = shared_connection
            ctx['shared_connection'] = shared_connection
        else:
            cc_list = []
        notify_send.delay(circle.owner, member, 'circle/messages/added_sitter', ctx=ctx, cc_user_list=cc_list)


class GroupJoinView(CircleJoinView):
    template_name = 'circle/group/join.html'
    form_valid_message = 'Successfully joined the group.'

    def dispatch(self, request, *args, **kwargs):
        self.dispatch_init()
        membership = self.existing_membership
        if membership:
            assert membership.is_valid_group_membership()
            if membership.is_disapproved():
                messages.error(request, 'Your are not allowed to join this group. Please contact the group administrators and have them manually add you into the group.')
                return permission_denied(request)
            elif membership.active:
                messages.info(request, 'You have already joined this group. Edit your membership here.')
                return redirect(reverse('circle:membership_edit_group', kwargs={'pk': membership.id}))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(type=Circle.Type.PUBLIC.value)

    def get_success_url(self):
        return reverse('circle:group_view', kwargs={'pk': self.get_object().id})

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['introduce'].widget = HiddenInput()
        form.fields['note'].label = 'Affiliation'
        form.fields['note'].help_text = 'What is your affiliation to the group? E.g., Jack\'s mon.'
        return form

    def form_valid(self, form):
        circle = self.get_object().to_proxy()
        target_user = self.get_user()
        circle.activate_membership(target_user)
        private_note = form.cleaned_data.get('private_note', None)
        as_rel = form.cleaned_data.get('as_rel', '')

        # save regardless of whether it's changed or not.
        membership = circle.get_membership(target_user)
        membership.private_note = private_note
        membership.as_rel = as_rel
        if form.cleaned_data.get('is_sitter', False):
            membership.as_role = UserRole.SITTER.value
        else:
            membership.as_role = UserRole.PARENT.value
        membership.save()

        introduce = form.cleaned_data.get('introduce', False)
        self.send_notification(target_user, circle, introduce)

        self.extra_process(membership)

        # this is not ModelView, and therefore membershihp is not automatically saved.
        return super().form_valid(form)

    def send_notification(self, member, circle, introduce):
        # will need to send a notification to circle admins to handle the request from "member"
        ctx = {
            'circle': circle,
            'member': member,
        }
        admin_list = circle.get_admin_users()
        notify_send.delay(member, admin_list, 'circle/messages/added_group', ctx=ctx)


# todo: this has potential problem. e.g., a member goes to the personal circle and change herself as "admin".
class MembershipEditView(LoginRequiredMixin, RegisteredRequiredMixin, AllowMembershipEditMixin, UpdateView):
    model = Membership
    form_class = MembershipEditForm
    template_name = 'circle/membership/edit.html'

    def get_membership(self):
        return self.get_object()

    # def form_valid(self, form):
    #     # self.redirect_url = form.cleaned_data['redirect']
    #     return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membership = self.get_membership()
        context['target_user'] = membership.member.to_puser()
        context['circle'] = membership.circle
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        membership = self.get_object()
        if membership.is_valid_parent_relation():
            form.fields['note'].label = 'Note & Endorsement'
            form.fields['as_admin'].label = 'Mark as a family member'
        elif membership.is_valid_sitter_relation():
            form.fields['note'].label = 'Note & Endorsement'
            form.fields['as_admin'].widget = HiddenInput()
            form.fields['as_admin'].initial = False
        return form

    # def get_initial(self):
    #     initial = super().get_initial()
    #     membership = self.get_membership()
    #     # set this to be automatically approve whenever the membership is edited
    #     if membership.is_pending_approval():
    #         initial['approved'] = True
    #     return initial

    def get_success_url(self):
        membership = self.get_object()
        if membership.is_valid_parent_relation() or membership.is_valid_sitter_relation():
            return reverse('account_view', kwargs={'pk': membership.member.id})
        return '/'


class GroupMembershipEditView(MembershipEditView):
    template_name = 'circle/membership/edit_group.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        membership = self.get_object()
        if membership.is_valid_group_membership():
            form.fields['note'].label = 'Group Affiliation'
            if self.request.puser.id in set([u.id for u in membership.circle.get_admin_users()]):
                form.fields['as_admin'].label = 'Mark as group administrator'
                # form.fields['as_admin'].help_text = 'This option available only to current administrators'
            else:
                form.fields['as_admin'].widget = HiddenInput()
        return form

    def get_success_url(self):
        membership = self.get_object()
        if membership.is_valid_group_membership():
            return reverse('circle:group_view', kwargs={'pk': membership.circle.id})
        return '/'


class MembershipApprovalView(LoginRequiredMixin, AllowMembershipEditMixin, DetailView):
    model = Membership
    context_object_name = 'membership'
    template_name = 'circle/membership/approval.html'

    def get_membership(self):
        return self.get_object()


# class ListMembersView(LoginRequiredMixin, RegisteredRequiredMixin, TemplateView):
#     template_name = 'circle/network.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         target_user = self.request.puser
#         if target_user.is_registered():
#             my_parents = list(Membership.objects.filter(circle=target_user.my_circle(Circle.Type.PARENT), active=True, approved=True).exclude(member=target_user).order_by('-updated'))
#             my_sitters = list(Membership.objects.filter(circle=target_user.my_circle(Circle.Type.SITTER), active=True, approved=True).exclude(member=target_user).order_by('-updated'))
#             context.update({
#                 'my_parents': my_parents,
#                 'my_sitters': my_sitters,
#             })
#         return context


class DiscoverView(LoginRequiredMixin, RegisteredRequiredMixin, DetailView):
    model = PUser
    context_object_name = 'target_user'
    template_name = 'circle/discover.html'
    display_limit = 12

    def get_object(self, queryset=None):
        return self.request.puser

    # the logic here is:
    # 1. find my friends (network)
    # 2. find my friends' friends who are not in my network
    # 3. if those people haven't disapproved me, then show them.
    def get_extended(self, as_role):
        me = self.object
        area = me.get_area()
        my_personal_circle = me.get_personal_circle(area=area)
        # my network (use to filter existing users)
        existing_membership = my_personal_circle.membership_set.filter(active=True).exclude(member=me)

        # my extended network
        my_parent_list = [m.member for m in my_personal_circle.membership_set.filter(active=True, as_role=UserRole.PARENT.value).exclude(approved=False).exclude(member=me)]
        extended_circle_list = Circle.objects.filter(owner__in=my_parent_list, type=my_personal_circle.type, area=my_personal_circle.area).values_list('id', flat=True)

        # my public network
        public_circle_list = me.membership_set.filter(circle__type=Circle.Type.PUBLIC.value, active=True, circle__area=me.get_area()).exclude(approved=False).values_list('circle__id', flat=True)

        combined_circle_list = list(extended_circle_list) + list(public_circle_list)

        # need to sort by member in order to use groupby.
        list_extended = Membership.objects.filter(active=True, approved=True, circle__id__in=combined_circle_list, as_role=as_role, member__info__area=area).exclude(member=me).exclude(member__id__in=existing_membership.values_list('member__id', flat=True)).order_by('member', '-updated')

        # build
        extended = []
        for member, membership_list in groupby(list_extended, lambda m: m.member):
            # if trust level is too low, then don't add.
            member_to_me = UserConnection(member, me)
            if member_to_me.trusted(TrustLevel.REMOTE):
                extended.append(UserConnection(me, member, list(membership_list)))
        extended.sort(key=lambda x: len(x.membership_list), reverse=True)

        return extended

    def get_extended_sitter(self):
        return self.get_extended(UserRole.SITTER.value)

    def get_extended_parent(self):
        return self.get_extended(UserRole.PARENT.value)

    def get_groups(self):
        me = self.object
        area = me.get_area()
        mapping = {m.circle: m for m in Membership.objects.filter(circle__type=Circle.Type.PUBLIC.value, member=me, active=True, circle__area=area).exclude(approved=False)}
        list_groups = []
        for circle in Circle.objects.filter(type=Circle.Type.PUBLIC.value, area=area, active=True).order_by('-updated', '-created'):
            if circle not in mapping:
                list_groups.append(circle)
        return list_groups

    def get_context_data(self, **kwargs):
        def process_list(t):
            mt = t[:display_max]
            random.shuffle(mt)
            return mt[:self.display_limit]

        context = super().get_context_data(**kwargs)
        display_max = self.display_limit * 2
        context.update({
            'circle': self.object.get_personal_circle(),
            'list_extended_sitter': process_list(self.get_extended_sitter()),
            'list_extended_parent': process_list(self.get_extended_parent()),
            'list_groups': self.get_groups()
        })
        return context


class BaseInviteView(LoginRequiredMixin, RegisteredRequiredMixin, CircleAdminMixin, TemplateView):
    template_name = 'circle/invite/base.html'

    def get_circle(self):
        return self.request.puser.get_personal_circle()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.puser
        context['circle'] = self.get_circle()
        return context


class ParentInviteView(BaseInviteView):
    template_name = 'circle/invite/parent.html'


class SitterInviteView(BaseInviteView):
    template_name = 'circle/invite/sitter.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sitter_checked_default'] = True
        return context


class GroupInviteView(BaseInviteView):
    template_name = 'circle/invite/group.html'

    def get_circle(self):
        return Circle.objects.get(pk=self.kwargs.get('pk', None))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_sitter_switch'] = True
        if self.get_circle().is_agency():
            context['sitter_checked_default'] = True
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
        personal_note = request.POST.get('personal_note', '')
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
                        # also set the default UserRole.
                        if as_role == UserRole.SITTER.value:
                            target_puser.info.role = as_role
                            target_puser.info.save()

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
                        # this should be a celery "delay" task. but for some reason the task is not discovered by celery.
                        circle_invite(circle, target_puser, current_user, personal_note)
                        processed_list.append(email)
                    else:
                        invalid_list.append(email)
                else:
                    invalid_list.append(email)

        if len(processed_list) > 0 and circle.is_type_personal():
            messages.success(request, 'Successfully added %s into your network.' % ', '.join(processed_list))
        elif len(processed_list) > 0 and circle.is_type_public():
            messages.success(request, 'Successfully added %s into the group.' % ', '.join(processed_list))
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


class ApproveMembership(LoginRequiredMixin, AllowMembershipEditMixin, SingleObjectMixin, JSONResponseMixin, AjaxResponseMixin, View):
    model = Membership

    def get_membership(self):
        return self.get_object()

    def post_ajax(self, request, *args, **kwargs):
        membership = self.get_membership()
        membership.circle.to_proxy().approve_membership(membership.member)
        membership.refresh_from_db()
        return self.render_json_response({'success': membership.approved})


class DisapproveMembership(LoginRequiredMixin, AllowMembershipEditMixin, SingleObjectMixin, JSONResponseMixin, AjaxResponseMixin, View):
    model = Membership

    def get_membership(self):
        return self.get_object()

    def post_ajax(self, request, *args, **kwargs):
        membership = self.get_membership()
        membership.circle.to_proxy().disapprove_membership(membership.member)
        membership.refresh_from_db()
        return self.render_json_response({'success': not membership.approved})
