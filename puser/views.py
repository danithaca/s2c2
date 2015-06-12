import tempfile
from account.mixins import LoginRequiredMixin
import account.views
import account.forms
from account.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import FormView, View, TemplateView
from formtools.wizard.views import SessionWizardView
from django.contrib import messages

from circle.forms import SignupFavoriteForm, ManageCircleForm, SignupConfirmForm, SignupCircleForm
from circle.models import Circle, Membership
from puser.forms import SignupBasicForm, UserInfoForm
from puser.models import PUser, Info


@login_required
def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return redirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL)


class LoginView(account.views.LoginView):
    form_class = account.forms.LoginEmailForm


class SignupView(account.views.SignupView):
    form_class = SignupBasicForm

    def generate_username(self, form):
        username = form.cleaned_data['email'].split('@')[0]
        return username


class UserEditView(LoginRequiredMixin, FormView):
    template_name = 'account/manage/default.html'
    form_class = UserInfoForm
    success_url = reverse_lazy('account_edit')

    def get_initial(self):
        # this will only work for current user.
        initial = super(UserEditView, self).get_initial()
        user = self.request.user
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
        return initial

    def get_form_kwargs(self):
        kwargs = super(UserEditView, self).get_form_kwargs()
        user = self.request.user
        try:
            kwargs['instance'] = user.info
        except Info.DoesNotExist:
            pass
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
            form.instance.initiated = True
            form.save()
        return super(UserEditView, self).form_valid(form)


class UserView(LoginRequiredMixin, TemplateView):
    template_name = 'account/view.html'


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
        kwargs['puser'] = PUser.from_user(self.request.user)
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