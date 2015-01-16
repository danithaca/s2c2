from django.contrib import auth, messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.forms import ModelForm, RegexField, TextInput, CheckboxSelectMultiple, ChoiceField
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from user.models import Profile, UserProfile



# keep session open for 3 days.
REMEMBER_ME_EXPIRY = 60 * 60 * 24 * 3


def signup(request):
    return signup_simple(request)


def signup_simple(request):
    class SimpleSignupForm(UserCreationForm):
        required_css_class = 'required'
        invitation_code = RegexField(
            label=_('Invitation code'),
            help_text=_('Signup is only available for people who have the correct invitation code.'),
            regex=r'^north$',
            error_messages={'invalid': _('Wrong invitation code. Please contact your coordinator.')},
            required=True,
            )

        def __init__(self, *args, **kwargs):
            super(SimpleSignupForm, self).__init__(*args, **kwargs)
            self.fields['email'].required = True

        class Meta:
            model = User
            fields = ('invitation_code', "username", 'password1', 'password2', 'email')

    class SignupView(FormView):
        template_name = 'user/signup_simple.jinja2'
        form_class = SimpleSignupForm
        success_url = reverse('user:edit')

        def form_valid(self, form):
            # this calls SignupForm::UserCreationForm::save()
            form.save()

            if not request.user.is_authenticated():
                # requires authentication() first.
                au = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
                auth.login(request, au)
                messages.success(request, 'Signup successful. Please edit your profile.')

            # this calls the default FormView::form_valid()
            return super(SignupView, self).form_valid(form)

    return SignupView.as_view()(request)


# def signup_full(request):
#
#     class UserForm(UserCreationForm):
#         required_css_class = 'required'
#         invitation_code = RegexField(
#             label=_('Invitation code'),
#             help_text=_('Signup is only available for people who have the correct invitation code.'),
#             regex=r'^north$',
#             error_messages={'invalid': _('Wrong invitation code. Please contact your coordinator.')},
#             required=True,
#             )
#
#         def __init__(self, *args, **kwargs):
#             super(UserForm, self).__init__(*args, **kwargs)
#             self.fields['email'].required = True
#             self.fields['first_name'].required = True
#             self.fields['last_name'].required = True
#
#         class Meta:
#             model = User
#             # by default, User->email is nullable, and allows duplicate.
#             # if we don't override form field here, the email setting would be like that.
#             fields = ('invitation_code', "username", 'password1', 'password2', 'first_name', 'last_name', 'email')
#
#             # doesn't work this way:
#             # required = {
#             #     'email': True,
#             #     'first_name': True,
#             #     'last_name': True,
#             # }
#
#     if request.method == 'POST':
#         form_user = UserForm(request.POST)
#         form_staff = ProfileForm(request.POST)
#         if form_user.is_valid() and form_staff.is_valid():
#             # save user and commit
#             u = form_user.save()
#             # u.first_name = form_staff.clean_data['first_name']
#             # u.last_name = form_staff.clean_data['last_name']
#
#             s = form_staff.save(commit=False)
#             s.user = u
#             s.save()
#             # this is required since we used commit=False first. see django documentation for details.
#             form_staff.save_m2m()
#
#             # login a user after signup
#             if not request.user.is_authenticated():
#                 # requires authentication() first.
#                 au = auth.authenticate(username=form_user.cleaned_data['username'], password=form_user.cleaned_data['password1'])
#                 auth.login(request, au)
#
#             return redirect('/')
#     else:
#         form_user = UserForm()
#         form_staff = ProfileForm()
#     return render(request, 'user/signup_full.jinja2', {'form_user': form_user, 'form_staff': form_staff})


# def signup(request):
#
#     class CenterStaffFrom(UserCreationForm):
#         required_css_class = 'required'
#         invitation_code = RegexField(
#             label=_('Invitation code'),
#             help_text=_('Signup is only available for people who have the correct invitation code.'),
#             regex=r'^north$',
#             error_messages={'invalid': _('Wrong invitation code. Please contact your coordinator.')},
#             required=True,
#             )
#
#         _phone_field_options = {
#             'regex': r'^\d\d\d-\d\d\d-\d\d\d\d$',
#             'error_messages': {'invalid': _('Please type in your phone number such as 734-555-5555.')}
#         }
#
#         phone_main = RegexField(
#             label=_('Phone number'),
#             help_text=_('10 digits phone number to contact you, e.g. 734-555-5555.'),
#             widget=TextInput(attrs={'placeholder': '555-555-5555'}),
#             **_phone_field_options
#         )
#
#         def __init__(self, *args, **kwargs):
#             super(CenterStaffFrom, self).__init__(*args, **kwargs)
#             self.fields['email'].required = True
#             self.fields['first_name'].required = True
#             self.fields['last_name'].required = True
#
#         class Meta:
#             model = FullUser
#             # by default, User->email is nullable, and allows duplicate.
#             # if we don't override form field here, the email setting would be like that.
#             fields = ('invitation_code', 'username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'phone_main', 'centers')
#             widgets = {
#                 'centers': CheckboxSelectMultiple()
#             }
#
#     class SignupView(FormView):
#         template_name = 'user/signup.jinja2'
#         form_class = CenterStaffFrom
#         success_url = '/'
#
#         def form_valid(self, form):
#             # this calls SignupForm::UserCreationForm::save()
#             form.save()
#             # this calls the default FormView::form_valid()
#             return super(SignupView, self).form_valid(form)
#
#     return SignupView.as_view()(request)


def login(request):
    # extra_context={'next': '/'} is not needed since we have settings.LOGIN_REDIRECT_URL
    response = auth_views.login(request, template_name='user/login.jinja2', authentication_form=AuthenticationForm)
    if isinstance(response, HttpResponseRedirect):
        messages.success(request, 'User %s logged in successfully.' % request.user.get_username())
        # someday: allow user set REMEMBER_ME later.
        request.session.set_expiry(REMEMBER_ME_EXPIRY)
    return response


# this will get called even in "admin", so we don't use it.
# @receiver(user_logged_in)
# def on_user_logged_in(sender, request, user, **kwargs):
#     messages.info(request, 'User %s logged in successfully.' % user.get_username())


@login_required
def logout(request):
    username = request.user.get_username() if request.user.is_authenticated() else None
    response = auth_views.logout(request, template_name='user/logout.jinja2', next_page='/')
    if username is not None and request.user.is_anonymous():
        messages.success(request, 'User %s logged out successfully.' % username)
    return response


# this will get called even in "admin", so we don't use it.
# @receiver(user_logged_out)
# def on_user_logged_out(sender, request, user, **kwargs):
#     messages.info(request, 'User %s logged out successfully.' % user.get_username())


# class StaffEditForm(StaffForm):
#     pass


# @login_required
# def edit(request):
#
#     class EditView(UpdateView):
#         model = FullUser
#         fields = ('first_name', 'last_name', 'email', 'phone_main', 'address', 'centers')
#         template_name = 'user/edit.jinja2'
#         success_url = '/'
#
#     edit_user = request.user
#     return EditView.as_view()(request, pk=edit_user.id)


@login_required
def edit(request):
    class UserEditForm(ModelForm):
        required_css_class = 'required'

        def __init__(self, *args, **kwargs):
            super(UserEditForm, self).__init__(*args, **kwargs)
            self.fields['email'].required = True
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

        class Meta:
            model = User
            fields = ('first_name', 'last_name', 'email')

    class ProfileForm(ModelForm):
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

        role = ChoiceField(label='My role', required=True,
                           choices=[('', '- Select -')] + [(g.pk, g.name) for g in Group.objects.all() if g.role.type_center is True])

        class Meta:
            model = Profile
            # todo: show "picture" and process it.
            fields = ('phone_main', 'address', 'centers', 'role', 'note')
            widgets = {
                'centers': CheckboxSelectMultiple()
                # 'centers': Select()
            }

    user_profile = UserProfile(request.user)

    if request.method == 'POST':
        form_user = UserEditForm(request.POST, instance=user_profile.user)
        form_profile = ProfileForm(request.POST, instance=user_profile.profile)

        if form_user.is_valid() and form_profile.is_valid():
            if form_user.has_changed():
                form_user.save()

            if form_profile.has_changed():
                if not user_profile.has_profile():
                    # assign the correct user instance to create a new Profile instance.
                    form_profile.instance.user = user_profile.user
                form_profile.save()

            if form_user.has_changed() or form_profile.has_changed():
                messages.success(request, 'Profile updated.')
            else:
                messages.warning(request, 'Nothing has updated.')
            return redirect('user:edit')
    else:
        form_user = UserEditForm(instance=user_profile.user)
        form_profile = ProfileForm(instance=user_profile.profile)

    return render(request, 'user/edit.jinja2', {'form_user': form_user, 'form_profile': form_profile})


def password_reset(request):
    redirect_url = '/'
    try:
        response = auth_views.password_reset(request,
            template_name='user/password_reset.jinja2',
            post_reset_redirect=redirect_url,
            email_template_name='user/email/password_reset_email.jinja2',
            subject_template_name='user/email/password_reset_subject.jinja2'
        )
        # note: auth.views.password_reset() doesn't tell you if the email exists or not for security reasons.
        if isinstance(response, HttpResponseRedirect):
            messages.success(request, 'Your request has been received. We will send you an email shortly if the email is valid.')
        return response
    except ConnectionRefusedError:
        messages.error(request, 'Email service is not configured. No email is sent out. Please report the bug to system admin.')
        # return server_error(request)
        return HttpResponseRedirect(redirect_url)


def password_reset_confirm(request, uidb64, token):
    response = auth_views.password_reset_confirm(request,  uidb64=uidb64, token=token,
        template_name='user/password_reset_confirm.jinja2', post_reset_redirect=reverse('login'))
    if isinstance(response, HttpResponseRedirect):
        messages.success(request, 'Password reset successfully. Please login using your new password.')
    return response


@login_required
def password_change(request):
    redirect_url = '/'
    response = auth_views.password_change(request,
        template_name='user/password_change.jinja2',
        post_change_redirect=redirect_url)
    if isinstance(response, HttpResponseRedirect):
        messages.success(request, 'Your password has changed successfully.')
    return response
