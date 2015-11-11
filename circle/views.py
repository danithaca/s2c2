from itertools import groupby
import json
import re

from account.mixins import LoginRequiredMixin
from braces.views import FormValidMessageMixin, UserPassesTestMixin, JSONResponseMixin, AjaxResponseMixin, \
    JSONRequestResponseMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse


# Create your views here.
from django.views.defaults import bad_request
from django.views.generic import FormView, CreateView, UpdateView, TemplateView, DetailView, View
from django.views.generic.detail import SingleObjectTemplateResponseMixin, SingleObjectMixin
from circle.forms import EmailListForm, UserConnectionForm, TagUserForm, CircleForm, MembershipForm, MembershipEditForm
from circle.models import Membership, Circle, ParentCircle, UserConnection, Friendship
from circle.tasks import circle_send_invitation
from puser.models import PUser
from p2.utils import RegisteredRequiredMixin, ControlledFormValidMessageMixin, UserRole, is_valid_email


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
        raise NotImplementedError()


################## regular views ####################


class CircleView(LoginRequiredMixin, RegisteredRequiredMixin, ControlledFormValidMessageMixin, DetailView):
    template_name = 'circle/view/base.html'
    context_object_name = 'circle'

    def add_extra_filter(self, queryset):
        raise NotImplementedError()


class PersonalCircleView(CircleView):
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
        my_parent_list = [m.member for m in list_membership.filter(approved=True)]    # only take approved=True (excluding approved=None)
        extended_circle_list = Circle.objects.filter(owner__in=my_parent_list, type=my_personal_circle.type, area=my_personal_circle.area)
        # need to sort by member in order to use groupby.
        extended = []
        list_extended = Membership.objects.filter(active=True, approved=True, circle__in=extended_circle_list).exclude(member=me).exclude(member__in=my_parent_list).order_by('member').order_by('-updated')
        list_extended = self.add_extra_filter(list_extended)
        for member, membership_list in groupby(list_extended, lambda m: m.member):
            extended.append(UserConnection(me, member, list(membership_list)))
        context['list_extended'] = extended

        context['full_access'] = True

        return context


class ParentCircleManageView(PersonalCircleView):
    template_name = 'circle/view/parent.html'
    # success_url = reverse_lazy('circle:parent')
    # form_valid_message = 'Parent connections successfully updated.'
    # # we always set "approved" to be true here.
    # default_approved = True
    #
    # def get_circle(self):
    #     circle = self.request.puser.my_circle(Circle.Type.PARENT)
    #     assert isinstance(circle, ParentCircle)
    #     return circle
    #
    # def get_membership_edit_form(self):
    #     form = MembershipEditForm(initial={'redirect': self.success_url})
    #     form.fields['note'].label = 'Endorsement'
    #     form.fields['type'].widget.choices = (
    #         (Membership.Type.NORMAL.value, 'Regular'),
    #         (Membership.Type.FAVORITE.value, 'Immediate family member (spouse, grandparents)'),
    #     )
    #     form.fields['type'].help_text = 'Mark as family member to allow Servuno propagate your job posts across social networks.'
    #     return form

    def add_extra_filter(self, queryset):
        return queryset.filter(as_role=UserRole.PARENT.value)


class BaseCircleView(LoginRequiredMixin, RegisteredRequiredMixin, ControlledFormValidMessageMixin, FormView):
    form_class = EmailListForm
    default_approved = None
    full_access = True

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
                    current_user = self.request.user.to_puser()     # this is to make a separate copy of the user to prevent "change dict" error at runtime
                    circle_send_invitation.delay(circle, target_puser, current_user)

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        email_qs = self.get_old_email_qs()
        initial['favorite'] = '\n'.join(list(email_qs))
        return initial

    def get_membership_edit_form(self):
        raise NotImplementedError()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['full_access'] = self.full_access
        if 'circle' not in context:
            context['circle'] = self.get_circle()
        context['edit_membership_form'] = self.get_membership_edit_form()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['full_access'] = self.full_access
        return kwargs


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

    def get_membership_edit_form(self):
        form = MembershipEditForm(initial={'redirect': self.success_url})
        form.fields['note'].label = 'Endorsement'
        form.fields['type'].widget.choices = (
            (Membership.Type.NORMAL.value, 'Regular'),
            (Membership.Type.FAVORITE.value, 'Immediate family member (spouse, grandparents)'),
        )
        form.fields['type'].help_text = 'Mark as family member to allow Servuno propagate your job posts across social networks.'
        return form


class SitterCircleView(BaseCircleView):
    template_name = 'circle/sitter.html'
    success_url = reverse_lazy('circle:sitter')
    form_valid_message = 'Successfully updated your paid babysitter connections.'
    # we always set "approved" to be true here.
    default_approved = True

    def get_circle(self):
        circle = self.request.puser.my_circle(Circle.Type.SITTER)
        return circle

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # find babysitter pool
    #     me = self.request.puser
    #     my_parent_circle = me.my_circle(Circle.Type.PARENT)
    #     my_parent_list = my_parent_circle.members.filter(membership__active=True, membership__approved=True).exclude(membership__member=me)
    #     other_parent_sitter_circle_list = Circle.objects.filter(owner__in=my_parent_list, type=Circle.Type.SITTER.value, area=my_parent_circle.area)
    #     # need to sort by member in order to use groupby.
    #     sitter_membership_pool = Membership.objects.filter(active=True, approved=True, circle__in=other_parent_sitter_circle_list).exclude(member=me).order_by('member')
    #     pool_list = []
    #     for member, membership_list in groupby(sitter_membership_pool, lambda m: m.member):
    #         pool_list.append(UserConnection(me, member, list(membership_list)))
    #     context['pool_list'] = pool_list
    #     return context

    def get_membership_edit_form(self):
        form = MembershipEditForm(initial={'redirect': self.success_url})
        form.fields['note'].label = 'Endorsement'
        form.fields['type'].widget.choices = (
            (Membership.Type.NORMAL.value, 'Regular'),
            (Membership.Type.FAVORITE.value, 'Preferred babysitter'),
        )
        form.fields['type'].help_text = 'Mark as preferred babysitter to instruct Servuno contact this person first when you make a job post.'
        return form


class TagCircleUserView(LoginRequiredMixin, RegisteredRequiredMixin, ControlledFormValidMessageMixin, FormView):
    form_class = TagUserForm
    template_name = 'circle/tag.html'
    success_url = reverse_lazy('circle:tag')
    form_valid_message = 'Successfully updated.'

    def form_valid(self, form):
        if form.has_changed():
            new_tags = set(form.cleaned_data['tags']) if 'tags' in form.cleaned_data else set([])
            old_tags = set(form.initial['tags']) if 'tags' in form.initial else set([])
            user = self.request.puser
            self.show_message = True

            for tag_circle in old_tags - new_tags:
                tag_circle.deactivate_membership(user)

            for tag_circle in new_tags - old_tags:
                tag_circle.activate_membership(user, approved=True)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_form'] = CircleForm()
        context['join_form'] = MembershipForm(initial={
            'member': self.request.puser,
            'active': True,
            'approved': True,
            'type': Membership.Type .NORMAL.value,
            'redirect': reverse('circle:tag'),
        })

        area = self.request.puser.get_area()
        mapping = {m.circle: m for m in Membership.objects.filter(circle__type=Circle.Type.TAG.value, member=self.request.puser, active=True, approved=True, circle__area=area)}
        context['all_tags'] = []
        for circle in Circle.objects.filter(type=Circle.Type.TAG.value, area=area):
            if circle in mapping:
                circle.user_membership = mapping[circle]
            context['all_tags'].append(circle)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['target_user'] = self.request.puser
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        tags = self.request.puser.get_tag_circle_set()
        if len(tags) > 0:
            initial['tags'] = list(tags)
        return initial


class TagAddView(LoginRequiredMixin, RegisteredRequiredMixin, CreateView):
    model = Circle
    form_class = CircleForm
    template_name = 'pages/basic_form.html'
    success_url = reverse_lazy('circle:tag')

    def form_valid(self, form):
        circle = form.instance
        circle.type = Circle.Type.TAG.value
        circle.owner = self.request.puser
        circle.area = self.request.puser.get_area()
        result = super().form_valid(form)
        # add the user who created the new group
        circle.activate_membership(self.request.puser, Membership.Type.ADMIN.value, True)
        return result


class TagEditView(LoginRequiredMixin, RegisteredRequiredMixin, UpdateView):
    model = Circle
    form_class = CircleForm
    template_name = 'pages/basic_form.html'

    def get_success_url(self):
        return reverse('circle:tag_view', kwargs={'pk': self.object.id})

    # def form_valid(self, form):
    #     circle = form.instance
    #     circle.type = Circle.Type.TAG.value
    #     circle.owner = self.request.puser
    #     circle.area = self.request.puser.get_area()
    #     return super().form_valid(form)


class CircleDetails(SingleObjectTemplateResponseMixin, SingleObjectMixin, BaseCircleView):
    type_constraint = None
    model = Circle
    template_name = 'circle/view.html'
    context_object_name = 'circle'

    form_valid_message = 'Added successfully.'
    # we always set "approved" to be true here.
    default_approved = True

    # we want to use DetailsView, but instead we used BaseCircleView. Therefore, here we override a little of DetailsView.get()
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            membership = self.object.get_membership(self.request.puser)
            if not membership.is_admin():
                self.full_access = False
        except:
            self.full_access = False
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.type_constraint is None or not isinstance(self.type_constraint, Circle.Type):
            return super().get_queryset()
        else:
            return Circle.objects.filter(type=self.type_constraint.value)

    # todo: this should move to BaseCircleView?
    def get_circle(self):
        return self.get_object()

    def get_old_email_qs(self):
        circle = self.get_circle()
        return Membership.objects.filter(circle=circle, active=True).order_by('updated').values_list('member__email', flat=True).distinct()

    def get_success_url(self):
        return reverse('circle:tag_view', kwargs={'pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        circle = self.get_object()
        current_membership = None
        if circle.is_valid_member(self.request.puser):
            current_membership = circle.get_membership(self.request.puser)
            context['current_membership'] = current_membership

        join_form = MembershipForm(initial={
            'circle': circle,
            'member': self.request.puser,
            'active': True,
            'approved': True,
            'type': Membership.Type.NORMAL.value,
            # 'note': None if current_membership is None else current_membership.note,
        }, instance=current_membership)

        context['join_form'] = join_form
        context['edit_form'] = CircleForm(instance=circle)
        return context

    def get_membership_edit_form(self):
        form = MembershipEditForm(initial={'redirect': self.get_success_url()})
        form.fields['note'].label = 'Group Affiliation'
        form.fields['type'].widget.choices = (
            (Membership.Type.NORMAL.value, 'Regular'),
            (Membership.Type.FAVORITE.value, 'Administrator'),
        )
        form.fields['type'].help_text = 'Mark as admin to allow the user make changes to the group.'
        return form


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


class MembershipUpdateView(LoginRequiredMixin, RegisteredRequiredMixin, CreateView):
    model = Membership
    form_class = MembershipForm
    template_name = 'pages/basic_form.html'

    default_active = True
    default_approved = True
    default_type = Membership.Type.NORMAL.value

    def dispatch(self, request, *args, **kwargs):
        self.current_user = request.puser
        self.circle = None
        self.existing_membership = None

        try:
            self.circle = Circle.objects.get(pk=kwargs.get('circle_id', None))
        except:
            pass
        if self.circle is None:
            return bad_request(request)

        try:
            # set existing_memberhip if any.
            self.existing_membership = Membership.objects.get(circle=self.circle, member=self.current_user)
        except:
            pass

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # if self.existing_membership is not None:
        #     self.existing_membership.active = form.cleaned_data['active']
        #     self.existing_membership.approved = form.cleaned_data['approved']
        #     self.existing_membership.note = form.cleaned_data['note']
        #     self.existing_membership.save()
        #     # this is called by CreateView.form_valid().
        #     return super(ModelFormMixin, self).form_valid(form)
        # else:
        #     return super().form_valid(form)
        self.redirect_url = form.cleaned_data['redirect']
        if 'leave' in form.data:
            form.instance.active = False
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {
            'circle': self.circle,
            'member': self.current_user,
            'active': self.default_active,
            'approved': self.default_approved,
            'type': self.default_type,
        }
        # this will make it a "Update", not "Create".
        if self.existing_membership is not None:
            kwargs['instance'] = self.existing_membership
        return kwargs

    def get_success_url(self):
        if self.redirect_url:
            return self.redirect_url
        else:
            return reverse('circle:tag_view', kwargs={'pk': self.circle.id})


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

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        membership = self.get_object()
        if membership.is_valid_parent_relation():
            form.fields['note'].label = 'Endorsement'
            form.fields['as_admin'].label = 'Mark as a family member'
        return form

    def get_success_url(self):
        membership = self.get_object()
        if membership.is_valid_parent_relation():
            return reverse('circle:parent')
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


class BasePoolView(LoginRequiredMixin, RegisteredRequiredMixin, TemplateView):
    template_name = 'circle/pool/base.html'
    circle_type = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # find babysitter pool
        me = self.request.puser
        my_parent_circle = me.my_circle(Circle.Type.PARENT)
        my_parent_list = my_parent_circle.members.filter(membership__active=True, membership__approved=True).exclude(membership__member=me)
        extended_circle_list = Circle.objects.filter(owner__in=my_parent_list, type=self.circle_type, area=my_parent_circle.area)
        # need to sort by member in order to use groupby.
        extended_membership_list = Membership.objects.filter(active=True, approved=True, circle__in=extended_circle_list).exclude(member=me).order_by('member')
        pool_list = []
        for member, membership_list in groupby(extended_membership_list, lambda m: m.member):
            pool_list.append(UserConnection(me, member, list(membership_list)))
        context['pool_list'] = pool_list
        return context


class SitterPoolView(BasePoolView):
    template_name = 'circle/pool/sitter.html'
    circle_type = Circle.Type.SITTER.value


class ParentPoolView(BasePoolView):
    template_name = 'circle/pool/parent.html'
    circle_type = Circle.Type.PARENT.value


################## views for API ########################


# note: this requires CircleAdminMixin, which is for Circle admins only
# this should not be used for regular users joining a public group, because they don't have CircleAdmin
class ActivateMembership(LoginRequiredMixin, CircleAdminMixin, SingleObjectMixin, JSONResponseMixin, AjaxResponseMixin, View):
    model = Circle

    def get_circle(self):
        return self.get_object()

    def post_ajax(self, request, *args, **kwargs):
        circle = self.get_circle().to_proxy()
        email_field = request.POST.get('email_field', None)
        is_sitter = request.POST.get('is_sitter', False)
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
                    if circle.is_type_public():
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
