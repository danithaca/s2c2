import tempfile

from account.mixins import LoginRequiredMixin
import account.views
import account.forms
from account.conf import settings
from braces.views import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, UpdateView, DetailView
from formtools.wizard.views import SessionWizardView

from django.contrib import messages
from rest_framework.generics import RetrieveAPIView

from circle.forms import SignupFavoriteForm, SignupCircleForm
from circle.models import Circle, Membership
from puser.forms import SignupBasicForm, UserInfoForm, SignupConfirmForm, UserPictureForm
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
    form_class = account.forms.LoginEmailForm


class SignupView(account.views.SignupView):
    form_class = SignupBasicForm

    def generate_username(self, form):
        return auto_user_name(form.cleaned_data['email'])


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


# This is obsolete in favor of the UpdateView approach.

# class UserPicture(LoginRequiredMixin, FormView):
#     """
#     User picture change view.
#     """
#     template_name = 'account/manage/default.html'
#     success_url = reverse_lazy('account_picture')
#     form_class = UserPictureForm
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         user = self.request.user
#         try:
#             kwargs['instance'] = user.info
#         except Info.DoesNotExist:
#             pass
#         return kwargs


class UserPicture(LoginRequiredMixin, UpdateView):
    """
    Handle user picture operations
    """
    template_name = 'account/manage/default.html'
    success_url = reverse_lazy('account_picture')
    model = Info
    # fields = ['picture_original', 'picture_cropping']
    form_class = UserPictureForm

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


class OnboardWizard(SessionWizardView):
    form_list = [
        ('basic', SignupBasicForm),
        ('info', UserInfoForm),
        ('favorite', SignupFavoriteForm),
        ('subscribe', SignupCircleForm),
        ('confirm', SignupConfirmForm),
    ]
    # template_name = 'account/onboard/onboard_default.html'

    file_storage = FileSystemStorage(tempfile.tempdir)

    step_meta_data = {
        'basic': {
            'title': 'Add basic info',
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
        'confirm': {
            'title': 'Confirm',
            'description': 'Review the information and sign up',
            'help_text': 'Click the button to confirm',
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


class APIGetByEmail(LoginRequiredMixin, RetrieveAPIView):
    lookup_field = 'email'
    serializer_class = UserSerializer
    queryset = PUser.objects.filter(is_active=True)
