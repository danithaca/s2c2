import account.views
import account.forms
from account.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.shortcuts import redirect, render
from formtools.wizard.views import SessionWizardView
from django.contrib import messages

from circle.forms import SignupFavoriteForm, SignupCircleForm


@login_required
def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return redirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL)


class LoginView(account.views.LoginView):
    form_class = account.forms.LoginEmailForm


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
        ('subscribe', SignupCircleForm),
        ('basic', account.views.SignupForm),
        ('favorite', SignupFavoriteForm),
    ]
    template_name = 'account/onboard.html'

    step_meta_data = {
        'basic': {
            'title': 'Add basic info',
            'description': 'Fill in basic account information'
        },
        'favorite': {
            'title': 'Add favorite people',
            'description': 'Add a list of people to your favorite list'
        },
        'subscribe': {
            'title': 'Join circles',
            'description': 'Join circles of people you trust'
        },
    }

    def get_context_data(self, form, **kwargs):
        context = super(OnboardWizard, self).get_context_data(form=form, **kwargs)
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
        return context

    def process_step(self, form):
        # this hook is post-process, meaning the current step is validated.
        # set status to be '' to avoid set as 'disabled'
        self.step_meta_data[self.steps.current]['status'] = ''
        return super(OnboardWizard, self).process_step(form)

    def done(self, form_list, form_dict, **kwargs):
        messages.success(self.request, 'Sign up successful. Please verify email.')
        return redirect('/')