from collections import OrderedDict
from account.mixins import LoginRequiredMixin
from account.models import SignupCode
import account.views
import account.forms
from account.conf import settings
from braces.views import UserPassesTestMixin, FormValidMessageMixin, AnonymousRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import forms as auth_forms
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, UpdateView, DetailView, CreateView
from django.views.generic.base import ContextMixin
from django.contrib import messages
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from circle.forms import UserConnectionForm
from circle.models import Circle, Membership
from circle.views import ParentCircleView, SitterCircleView, TagCircleUserView
from login_token.models import Token
from login_token.conf import settings as login_token_settings
from p2.utils import RegisteredRequiredMixin
from puser.forms import UserInfoForm, UserPictureForm, LoginEmailAdvForm, UserInfoOnboardForm, \
    SignupFullForm, WaitingForm
from puser.models import Info, PUser, Waiting
from puser.serializers import UserSerializer
from shout.tasks import notify_send
from p2.utils import auto_user_name


@login_required
def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return redirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL)


class LoginView(account.views.LoginView):
    # switching to use Email-only login form
    form_class = LoginEmailAdvForm

    def get_initial(self):
        initial = super().get_initial()
        if 'email' in self.request.GET:
            initial['email'] = self.request.GET['email']
        return initial


class SimpleChangePasswordView(account.views.ChangePasswordView):
    form_class = auth_forms.SetPasswordForm

    def form_valid(self, form):
        form.cleaned_data['password_new'] = form.cleaned_data['new_password1']
        return super().form_valid(form)


class UserEdit(LoginRequiredMixin, FormView):
    """
    The view to handle user edit.
    """
    template_name = 'account/manage/default.html'
    form_class = UserInfoForm
    success_url = reverse_lazy('account_view')

    def get_initial(self):
        # this will only work for current user.
        initial = super().get_initial()
        user = self.request.user
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
        initial['email'] = user.email
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        puser = self.request.puser
        kwargs['instance'] = puser.get_info()
        return kwargs

    def form_valid(self, form):
        if form.has_changed():
            user = self.request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            # save for the Info instance.
            if form.instance.user is None or form.instance.user != user:
                form.instance.user = user
            # if user edit profile, definitely set initiated to be True
            # todo: think more about how to set "initiated" or just use 'active' instead.
            form.instance.initiated = True
            form.save()

            messages.success(self.request, 'Profile successfully updated.')
        return super(UserEdit, self).form_valid(form)


class InviteView(AnonymousRequiredMixin, FormView):
    form_class = WaitingForm
    template_name = 'account/invite.html'
    authenticated_redirect_url = reverse_lazy('account_view')
    success_url = '/'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            existing_user = PUser.get_by_email(email)
            if existing_user.is_registered():
                # if user is a registered user => go to login with the email
                messages.info(self.request, 'A user with email %s is already signed up. Please log in instead.' % email)
                return HttpResponseRedirect('%s?email=%s' % (reverse('account_login'), email))
            else:
                # if pre-registered => send email with signup info
                notify_send.delay(None, existing_user, 'account/email/invite_instructions')
                messages.info(self.request, 'Our record shows that the email %s is pre-registered. An email has been sent out with instrucions on how to sign up and log in to the site.' % email)
                return redirect('account_invite')
        except:
            # email is not associated with an existing user
            # regardless of what we do, first save to waiting list if not in it yet.
            if not Waiting.objects.filter(email=email).exists():
                Waiting.objects.create(email=email)

            # try signup code
            code_str = form.cleaned_data['invitation_code']
            if code_str:
                try:
                    SignupCode.check_code(code_str)
                    # now there is a valid code
                    # => regardless of whether the email is in waiting list or not, redirect to signup.
                    redirect_url = '%s?code=%s&email=%s' % (reverse('account_signup'), code_str, email)
                    return HttpResponseRedirect(redirect_url)
                except SignupCode.InvalidCode:
                    pass

            # there is not a valid code_str => redirect to '/'
            messages.info(self.request, 'Thank you! Your email is added to the wait list.')
            return HttpResponseRedirect(self.success_url)


class UserPicture(LoginRequiredMixin, FormValidMessageMixin, UpdateView):
    """
    Handle user picture operations
    """
    template_name = 'account/manage/default.html'
    success_url = reverse_lazy('account_picture')
    model = Info
    # fields = ['picture_original', 'picture_cropping']
    form_class = UserPictureForm
    form_valid_message = 'Picture updated.'

    def get_object(self, queryset=None):
        puser = self.request.puser
        return puser.get_info()


class TrustedUserMixin(UserPassesTestMixin):
    """
    This only works in DetailsView where PUser is the object.
    """
    raise_exception = True

    def test_func(self, user):
        target_user = self.get_object()
        # the target user (whom the current user is viewing) needs to trust the current user.
        return target_user.trusted(user)


class UserView(LoginRequiredMixin, RegisteredRequiredMixin, TrustedUserMixin, DetailView):
    """
    The main thing to display user profile.
    """
    template_name = 'account/view.html'
    model = PUser
    context_object_name = 'target_user'

    def get_object(self, queryset=None):
        try:
            obj = super().get_object(queryset)
        except AttributeError:
            obj = self.request.puser
        return obj

    def get_context_data(self, **kwargs):
        u = self.get_object()
        context = {
            'current_user': self.request.puser,
            'full_access': self.get_object() == self.request.puser,
        }

        if u != self.request.puser:
            context.update({
                'interactions': self.request.puser.count_interactions(u),
                'current_user_shared_circles': self.request.puser.get_shared_connection(u).get_circle_list(),
                'user_connection_form': UserConnectionForm(initiate_user=self.request.puser, target_user=u),
            })

        if u.is_registered() and u.has_area():
            area = u.get_area()
            # in_others = list(PUser.objects.filter(owner__type=Circle.Type.PERSONAL.value, owner__area=area, owner__membership__member=u, owner__membership__active=True, owner__membership__approved=True).exclude(owner__owner=u).distinct())
            # my_listed = list(PUser.objects.filter(membership__circle__owner=u, membership__circle__area=area, membership__circle__type=Circle.Type.PERSONAL.value, membership__active=True, membership__approved=True).exclude(membership__member=u).distinct())
            # my_circles = list(Circle.objects.filter(membership__member=u, membership__circle__type=Circle.Type.PUBLIC.value, membership__circle__area=area, membership__active=True, membership__approved=True).distinct())
            # my_memberships = list(Membership.objects.filter(member=u, circle__type=Circle.Type.PUBLIC.value, circle__area=area, active=True))
            # my_agencies = list(Membership.objects.filter(member=u, circle__type=Circle.Type.AGENCY.value, circle__area=area, active=True))

            my_parents = list(Membership.objects.filter(circle=u.my_circle(Circle.Type.PARENT), active=True, approved=True).exclude(member=u).order_by('created'))
            my_sitters = list(Membership.objects.filter(circle=u.my_circle(Circle.Type.SITTER), active=True, approved=True).exclude(member=u).order_by('created'))
            my_memberships = list(Membership.objects.filter(member=u, circle__type=Circle.Type.TAG.value, circle__area=area, active=True))

            context.update({
                # 'in_others': in_others,
                # 'my_listed': my_listed,
                # 'my_circles': my_circles,
                'my_memberships': my_memberships,
                # 'my_agencies': my_agencies,
                'my_parents': my_parents,
                'my_sitters': my_sitters,
            })

        # # favors karma
        # karma = defaultdict(int)
        # for favor in u.engagement_favors():
        #     direction = 0
        #     if favor.is_main_contract():
        #         direction = -1
        #     elif favor.is_match_confirmed():
        #         direction = 1
        #     karma[favor.passive_user()] += direction
        # context['favors_karma'] = [(u, f) for u, f in karma.items() if f != 0]

        context.update(kwargs)
        return super().get_context_data(**context)


# this is perhaps not needed anymore. we'll make sure email works in all environment.

# class PasswordResetView(account.views.PasswordResetView):
#     def send_email(self, email):
#         try:
#             super(PasswordResetView, self).send_email(email)
#             messages.success(self.request, 'Password reset sent.</a>')
#         except ConnectionRefusedError as e:
#             messages.warning(self.request, 'Cannot connect to email service.')


#################### views for onboarding ######################


class MultiStepViewsMixin(ContextMixin):
    """
    This is to help with multiple views, different from FormWizard
    """

    final_url = reverse_lazy('tour')

    @classmethod
    def get_steps_meta(cls):
        step_order = ['SignupView', 'OnboardParentCircle', 'OnboardTagCircle']
        step_url = [reverse('account_signup'), reverse('onboard_parent'), reverse('onboard_group')]
        next_step_url = list(step_url)
        next_step_url.append(cls.final_url)
        del(next_step_url[0])
        steps_meta = OrderedDict()
        for name, url, next_url in zip(step_order, step_url, next_step_url):
            steps_meta[name] = {'url': url, 'next_url': next_url}
        return steps_meta

    # def get_step_url(self):
    #     assert hasattr(self, 'step_url')
    #     return self.step_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['step_title'] = self.get_step_title()
        context['step_note'] = self.get_step_note()

        # update steps meta with position info
        steps_meta = self.get_steps_meta()
        current_step_name = self.__class__.__name__
        position = -1
        for step_name in steps_meta:
            if step_name == current_step_name:
                steps_meta[step_name]['position'] = 0
                position = 1
            else:
                steps_meta[step_name]['position'] = position
        context['steps_meta'] = steps_meta

        return context

    @classmethod
    def get_next_step_url(cls):
        steps_meta = cls.get_steps_meta()
        current_step_name = cls.__name__
        return steps_meta[current_step_name]['next_url']

    # this only works for FormView where sucess_url is needed.
    def get_success_url(self):
        return self.get_next_step_url()

    def get_step_title(self):
        if hasattr(self, 'step_title'):
            return self.step_title
        else:
            return ''

    def get_step_note(self):
        if hasattr(self, 'step_note'):
            return self.step_note
        else:
            return ''


class SignupView(MultiStepViewsMixin, account.views.SignupView):
    step_title = 'Create an Account'
    step_note = 'Your information is only visible to people in your network.'
    form_class = SignupFullForm

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            self.created_user = self.request.user
        if not self.is_open():
            return self.closed()
        return super(account.views.SignupView, self).post(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            self.created_user = self.request.user
        if not self.is_open():
            return self.closed()
        return super(account.views.SignupView, self).post(*args, **kwargs)

    def is_open(self):
        if self.created_user:
            return True
        return super().is_open()

    def closed(self):
        return redirect('account_invite')

    def generate_username(self, form):
        return auto_user_name(form.cleaned_data['email'])

    def send_email_confirmation(self, email_address):
        # confirmation email is sent blocking. not through Notify.
        # could override here, or use a different Account Hookset
        super().send_email_confirmation(email_address)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.created_user:
            kwargs['instance'] = self.created_user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if 'email' not in initial and 'email' in self.request.GET:
            initial['email'] = self.request.GET['email']
        return initial

    def form_valid(self, form):
        if self.created_user:
            # account already created earlier. need to: 1) set password, 2) set names, 3) set info
            existing_user = self.created_user
            password = form.cleaned_data.get("password")
            existing_user.set_password(password)
            existing_user.save()

            # mark email verified, because the only way to login here is to click email
            # todo: or is it?
            existing_user.emailaddress_set.filter(email=existing_user.email, verified=False).update(verified=True)

            self.after_signup(form)
            self.form = form
            self.login_user()
            redirection = redirect(self.get_success_url())
        else:
            # super() only save the basic user account: email/username/password and Account/EmailAddress
            redirection = super().form_valid(form)

        # we'll need to do some other work here.
        # save first_name, last_name
        self.created_user.first_name = form.cleaned_data['first_name']
        self.created_user.last_name = form.cleaned_data['last_name']
        self.created_user.save()
        # update area
        info = self.created_user.to_puser().get_info()
        info.registered = True          # registered is always True after successfully go thru this step.
        info.set_area(form.cleaned_data['area'])
        info.save()

        # send admin notice
        notify_send.delay(None, None, 'account/email/admin_new_user_signup', ctx={'user': self.created_user})
        return redirection


class OnboardAbout(MultiStepViewsMixin, TemplateView):
    template_name = 'account/onboard/about.html'


class OnboardProfile(MultiStepViewsMixin, UserEdit):
    template_name = 'account/onboard/form.html'
    step_title = 'Update Profile'
    form_class = UserInfoOnboardForm


class OnboardParentCircle(MultiStepViewsMixin, ParentCircleView):
    template_name = 'account/onboard/parent.html'
    step_title = 'Connect to Parents'
    step_note = 'Add other parents your trust who can babysit for you occasionally on the basis of reciprocity. DO NOT add anyone you don\'t trust.'


class OnboardSitterCircle(MultiStepViewsMixin, SitterCircleView):
    template_name = 'account/onboard/sitter.html'
    step_title = 'Add Paid Babysitters (Optional)'
    step_note = 'Add babysitters you trust, e.g, grandparents, teenage cousins, and/or professional babysitters you used before. They will be shared among your parents connections added in the previous step. DO NOT add anyone you don\'t trust.'
    # form_valid_message = "Welcome! You can find a babysitter now or wait for others to find help from you."
    # show_message = True


class OnboardTagCircle(MultiStepViewsMixin, TagCircleUserView):
    template_name = 'account/onboard/group.html'
    step_title = 'Join Parents Groups'
    step_note = 'Join groups to meet new parents.'
    form_valid_message = ''
    # show_message = True


class OnboardPicture(MultiStepViewsMixin, UserPicture):
    template_name = 'account/onboard/form.html'
    form_valid_message = "Welcome! You can find a babysitter now or wait for others to find help from you."
    step_title = 'Upload Picture'
    # step_note = 'Let other users see you!'


################## views for API ########################


class APIGetByEmail(LoginRequiredMixin, RetrieveAPIView):
    lookup_field = 'email'
    serializer_class = UserSerializer
    queryset = PUser.objects.filter(is_active=True)
    # queryset = PUser.objects.filter(is_active=True)

    # purpose of the override is to add "membership note" if there's a Circle parameter
    def retrieve(self, request, *args, **kwargs):
        circle_id = request.GET.get('circle', None)
        if circle_id:
            try:
                circle = Circle.objects.get(pk=circle_id)
                target_user = self.get_object()
                membership = circle.get_membership(target_user)
                serializer = self.get_serializer(target_user)
                data = serializer.data
                data['membership_id'] = membership.id
                data['membership_type'] = membership.type
                if membership.note:
                    data['note'] = membership.note
                if membership.type == Membership.Type.FAVORITE.value or membership.is_admin():
                    data['star'] = True
                # the only alternative that doesn't do super().
                return Response(data)
            except:
                pass
        return super().retrieve(request, *args, **kwargs)
