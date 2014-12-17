from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.contrib.formtools.wizard.views import SessionWizardView
from django.forms import ModelForm, CharField, RegexField, TextInput, CheckboxSelectMultiple
from django.shortcuts import render, redirect
from django.views.generic import FormView
from user.models import Staff
from django.utils.translation import ugettext_lazy as _


class UserForm(UserCreationForm):
    required_css_class = 'required'
    invitation_code = RegexField(
        label=_('Invitation code'),
        help_text=_('Signup is only available for people who have the correct invitation code.'),
        regex=r'^north$',
        error_messages={'invalid': _('Wrong invitation code. Please contact your coordinator.')},
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta:
        model = User
        # by default, User->email is nullable, and allows duplicate.
        # if we don't override form field here, the email setting would be like that.
        fields = ('invitation_code', "username", 'password1', 'password2', 'first_name', 'last_name', 'email')

        # doesn't work this way:
        # required = {
        #     'email': True,
        #     'first_name': True,
        #     'last_name': True,
        # }


class StaffForm(ModelForm):
    required_css_class = 'required'

    _phone_field_options = {
        'regex': r'^\d\d\d-\d\d\d-\d\d\d\d$',
        'error_messages': {'invalid': _('Please type in your phone number such as 734-555-5555.')}
    }

    phone_main = RegexField(
        label=_('Phone number'),
        help_text=_('10 digits phone number to contact you, e.g. 734-555-5555.'),
        widget=TextInput(attrs={'placeholder': '555-555-5555'}),
        **_phone_field_options
    )

    class Meta:
        model = Staff
        fields = ('phone_main', 'address', 'role', 'centers')
        widgets = {
            'centers': CheckboxSelectMultiple()
        }


# class SignupView(FormView):
#     template_name = 'user/signup.jinja2'
#     #form_class = SignupForm
#     form_class = StaffForm
#     success_url = '/'
#
#     def form_valid(self, form):
#         # this calls SignupForm::UserCreationForm::save()
#         form.save()
#         # this calls the default FormView::form_valid()
#         return super(SignupView, self).form_valid(form)


# class SignupWizardView(SessionWizardView):
#     pass


def signup(request):
    if request.method == 'POST':
        form_user = UserForm(request.POST)
        form_staff = StaffForm(request.POST)
        if form_user.is_valid() and form_staff.is_valid():
            # save user and commit
            u = form_user.save()
            # u.first_name = form_staff.clean_data['first_name']
            # u.last_name = form_staff.clean_data['last_name']

            s = form_staff.save(commit=False)
            s.user = u
            s.save()
            # this is required since we used commit=False first. see django documentation for details.
            form_staff.save_m2m()

            return redirect('/')
    else:
        form_user = UserForm()
        form_staff = StaffForm()
    return render(request, 'user/signup.jinja2', {'form_user': form_user, 'form_staff': form_staff})


def login(request):
    return auth_views.login(request, template_name='user/login.jinja2', extra_context={'next': '/'})