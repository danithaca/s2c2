import tempfile

from account.mixins import LoginRequiredMixin
import account.views
import account.forms
from account.conf import settings
from braces.views import UserPassesTestMixin, FormValidMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, UpdateView, DetailView
from formtools.wizard.views import SessionWizardView

from django.contrib import messages
from rest_framework.generics import RetrieveAPIView

from circle.forms import SignupFavoriteForm, SignupCircleForm, ManagePersonalForm
from circle.models import Circle, Membership
from circle.views import ManagePersonal, ManagePublic
from puser.forms import SignupBasicForm, UserInfoForm, SignupConfirmForm, UserPictureForm, LoginEmailAdvForm
from puser.models import Info, PUser
from puser.serializers import UserSerializer
from s2c2.utils import auto_user_name


@login_required
def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return redirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL)


class LoginView(account.views.LoginView):
    # switching to use Email-only login form
    form_class = LoginEmailAdvForm


class SignupView(account.views.SignupView):
    form_class = SignupBasicForm

    def generate_username(self, form):
        return auto_user_name(form.cleaned_data['email'])

    def send_email_confirmation(self, email_address):
        # confirmation email is sent blocking. not through Notify.
        # could override here, or use a different Account Hookset
        super().send_email_confirmation(email_address)

    # this allows the default email field for Signup code not permitting user change the email address
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.signup_code:
            form.fields['email'].widget.attrs = {
                'readonly': True
            }
        return form

    # SignupBasicForm (subclass of Account.SignupForm) checks email existence using EmailAddress
    # a dummy user won't have "EmailAddress" and therefore should be pass form validation.
    # we'll still have to take care of "create_user" when dummy user alreay exists.
    def create_user(self, form, commit=True, **kwargs):
        email = form.cleaned_data["email"].strip()
        try:
            user = PUser.get_by_email(email)
            if self.signup_code:
                self.request.session['signup_inviter_email'] = self.signup_code.inviter.email
            # even if there's no signup_code, we still allow signup if "active" is not set.
            # if self.signup_code and self.signup_code.email == email and not user.is_active:
            if not user.is_active:
                user.is_active = True
                password = form.cleaned_data.get("password")
                if password:
                    user.set_password(password)
                else:
                    user.set_unusable_password()
                if commit:
                    user.save()
                return user
        except PUser.DoesNotExist:
            pass
        return super().create_user(form, commit, **kwargs)


class UserEdit(LoginRequiredMixin, FormView):
    """
    The view to handle user edit.
    """
    template_name = 'account/manage/default.html'
    form_class = UserInfoForm
    success_url = reverse_lazy('account_edit')

    def get_initial(self):
        # this will only work for current user.
        initial = super().get_initial()
        user = self.request.user
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
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


class UserView(LoginRequiredMixin, TrustedUserMixin, DetailView):
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
        in_others = list(PUser.objects.filter(owner__type=Circle.Type.PERSONAL.value, owner__membership__member=u, owner__membership__active=True, owner__membership__approved=True).exclude(owner__owner=u).distinct())
        my_listed = list(PUser.objects.filter(membership__circle__owner=u, membership__circle__type=Circle.Type.PERSONAL.value, membership__active=True, membership__approved=True).exclude(membership__member=u).distinct())
        my_circles = list(Circle.objects.filter(membership__member=u, membership__circle__type=Circle.Type.PUBLIC.value, membership__active=True, membership__approved=True).distinct())
        my_memberships = list(Membership.objects.filter(member=u, circle__type=Circle.Type.PUBLIC.value, active=True))
        context = {
            'full_access': self.get_object() == self.request.puser,
            'in_others': in_others,
            'my_listed': my_listed,
            'my_circles': my_circles,
            'my_memberships': my_memberships
        }
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


class MultiStepViewsMixin(object):
    """
    This is to help with multiple views, different from FormWizard
    """


# class OnboardSignup(MultiStepViewsMixin, SignupView):
#     pass
    # this is not used because SignupView reloaded get_success_url(). Set SIGNUP REDIRECT URL instead.
    # success_url = reverse_lazy('onboard_profile')

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated():
    #         if request.method.lower() == 'get':
    #             return
    #     return super().dispatch(request, *args, **kwargs)

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     if self.request.user.is_authenticated():
    #         for field_name in form.fields:
    #             form.fields[field_name].widget.attrs['readonly'] = True
    #     return form


class OnboardProfile(MultiStepViewsMixin, UserEdit):
    template_name = 'account/onboard/base.html'
    success_url = reverse_lazy('onboard_personal')


class OnboardPersonalCircle(MultiStepViewsMixin, ManagePersonal):
    template_name = 'account/onboard/manage_personal.html'
    success_url = reverse_lazy('onboard_public')

    def get_initial(self):
        initial = super().get_initial()
        # if initial['faovorite'] already exists, we don't override it.
        if not initial.get('favorite', '') and self.request.session.get('signup_inviter_email', ''):
            initial['favorite'] = self.request.session['signup_inviter_email']
            initial['force_save'] = True
        return initial


class OnboardPublicCircle(MultiStepViewsMixin, ManagePublic):
    template_name = 'account/onboard/manage_public.html'
    success_url = reverse_lazy('onboard_picture')


class OnboardPicture(MultiStepViewsMixin, UserPicture):
    template_name = 'account/onboard/base.html'
    success_url = '/'
    form_valid_message = "Welcome! You can find a babysitter or wait for others to find help from you. Manage your contacts and circles by following your account link on the top right corner."


# deprecated in favor of multiple formviews.
class OnboardWizard(SessionWizardView):
    form_list = [
        ('basic', SignupBasicForm),
        ('info', UserInfoForm),
        ('favorite', SignupFavoriteForm),
        ('subscribe', SignupCircleForm),
    ]
    # template_name = 'account/onboard/onboard_default.html'

    file_storage = FileSystemStorage(tempfile.tempdir)

    step_meta_data = {
        'basic': {
            'title': 'Create an account',
            'description': 'Fill in basic account information',
            'help_text': 'Please fill in basic account information',
        },
        'info': {
            'title': 'Edit profile',
            'description': 'Fill in basic account information',
            'help_text': 'Please fill in basic account information',
        },
        'favorite': {
            'title': 'Add favorite people',
            'description': 'Add a list of people to your favorite list',
            'help_text': 'Add a list of people to your favorite list',
        },
        'subscribe': {
            'title': 'Join circles',
            'description': 'Join circles of people you trust',
            'help_text': 'Subscribe to a few circles to allow peoples in the trusted circles babysit for you.',
            'template': 'account/onboard/onboard_subscribe.html',
        },
    }

    def get_context_data(self, form, **kwargs):
        context = super(OnboardWizard, self).get_context_data(form=form, **kwargs)

        # process all steps meta data to display the vertical tabs
        context['step_meta_data'] = []
        for i, f in enumerate(self.form_list):
            # have to be pass by value
            d = {}
            d.update(self.step_meta_data[f])

            d['step'] = i + 1
            if self.steps.current == f:
                d['status'] = 'active'
            elif 'status' in d:
                # do nothing. keep the status as is
                pass
            else:
                d['status'] = 'disabled'

            context['step_meta_data'].append(d)

        # add the current step meta data
        context['current_step_meta_data'] = self.step_meta_data[self.steps.current]

        return context

    def process_step(self, form):
        # this hook is post-process, meaning the current step is validated.
        # set status to be '' to avoid set as 'disabled'
        self.step_meta_data[self.steps.current]['status'] = ''
        return super(OnboardWizard, self).process_step(form)

    def get_template_names(self):
        return self.step_meta_data[self.steps.current].get('template', 'account/onboard/onboard_default.html')

    def done(self, form_list, form_dict, **kwargs):
        messages.success(self.request, 'Sign up successful. Please verify email.')
        return redirect('/')


################## views for API ########################


class APIGetByEmail(LoginRequiredMixin, RetrieveAPIView):
    lookup_field = 'email'
    serializer_class = UserSerializer
    queryset = PUser.objects.filter(is_active=True)
