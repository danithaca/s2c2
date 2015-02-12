from django.contrib import auth, messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.forms import ModelForm, RegexField, TextInput, CheckboxSelectMultiple, ChoiceField, Form, \
    MultipleChoiceField
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from log.models import Log
from s2c2.decorators import user_is_center_manager, user_is_verified, user_is_me_or_same_center
from s2c2.utils import dummy
from s2c2.widgets import InlineCheckboxSelectMultiple, USPhoneNumberWidget

from user.models import Profile, UserProfile, GroupRole


# keep session open for 12 hours.
REMEMBER_ME_EXPIRY = 60 * 60 * 12


class DefaultUserMixin(SingleObjectMixin):
    model = User
    pk_url_kwarg = 'uid'

    def get_object(self, queryset=None):
        try:
            super(DefaultUserMixin, self).get_object(queryset)
        except AttributeError as e:
            # using this in Views will have the request object in self.
            return self.request.user


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
            # email is required to reset password, etc.
            self.fields['email'].required = True

        class Meta:
            model = User
            fields = ('invitation_code', "username", 'password1', 'password2', 'email')

    class SignupView(FormView):
        template_name = 'user/signup_simple.html'
        form_class = SimpleSignupForm
        success_url = reverse('user:edit')

        def form_valid(self, form):
            # this calls SignupForm::UserCreationForm::save()
            form.save()
            u = form.instance
            Log.create(Log.SIGNUP, u, [u])

            if not request.user.is_authenticated():
                # requires authentication() first.
                au = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
                auth.login(request, au)
                messages.success(request, 'Sign up successful. Please edit your profile to get verification from the center\'s managers.')

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
#     return render(request, 'user/signup_full.html', {'form_user': form_user, 'form_staff': form_staff})


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
#         template_name = 'user/signup.html'
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


class ExAuthenticationForm(AuthenticationForm):
    """ Allows log in with either username or email """
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        # this is the hack that allows email
        if '@' in username:
            try:
                actual_username = User.objects.filter(email=username).values_list('username', flat=True).first()
                if actual_username:
                    username = actual_username
            except User.DoesNotExist:
                pass

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                    )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


def login(request):
    # extra_context={'next': '/'} is not needed since we have settings.LOGIN_REDIRECT_URL
    response = auth_views.login(request, template_name='user/login.html', authentication_form=ExAuthenticationForm)
    if isinstance(response, HttpResponseRedirect):
        # messages.success(request, 'User %s logged in successfully.' % request.user.get_username())
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
    response = auth_views.logout(request, template_name='user/logout.html', next_page='/')
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
#         template_name = 'user/edit.html'
#         success_url = '/'
#
#     edit_user = request.user
#     return EditView.as_view()(request, pk=edit_user.id)


@login_required
def edit(request):
    user_profile = UserProfile(request.user)
    gr = user_profile.get_center_role()
    role_initial_id = gr.group.pk if gr is not None else 0

    class UserEditForm(ModelForm):
        required_css_class = 'required'

        def __init__(self, *args, **kwargs):
            super(UserEditForm, self).__init__(*args, **kwargs)
            self.fields['email'].required = True
            # self.fields['first_name'].required = True
            # self.fields['last_name'].required = True

        class Meta:
            model = User
            fields = ('email', 'first_name', 'last_name')
            labels = {
                'email': 'Email',
            }

    class ProfileForm(ModelForm):
        required_css_class = 'required'

        # _phone_field_options = {
        #     'regex': r'^\d\d\d-\d\d\d-\d\d\d\d$',
        #     'error_messages': {'invalid': _('Please type in your phone number such as 734-555-5555.')}
        # }
        #
        # phone_main = RegexField(
        #     label=_('Phone number'),
        #     help_text=_('10 digits phone number to contact you, e.g. 734-555-5555.'),
        #     widget=TextInput(attrs={'placeholder': '555-555-5555'}),
        #     **_phone_field_options
        # )

        role = forms.TypedChoiceField(label='Employment role', required=False, coerce=int, empty_value=0,
                                      choices=GroupRole.get_center_roles_choices(), initial=role_initial_id,
                                      help_text='Please select your role with the center. Changing role needs verification from the managers.')

        class Meta:
            model = Profile
            # todo: show "picture" and process it.
            fields = ('phone_main', 'phone_backup', 'address', 'centers', 'role', 'note')
            widgets = {
                'centers': InlineCheckboxSelectMultiple,
                'phone_main': USPhoneNumberWidget,
                'phone_backup': USPhoneNumberWidget,
                # 'centers': Select()
            }
            help_texts = {
                'centers': 'Select the children\'s center(s) your are affiliated with.',
                'phone_main': 'The main phone number to contact you. E.g. 734-123-1234.',
                'phone_backup': 'Optional backup phone number. E.g. 734-123-1234.',
                'address': 'Your address may be needed for verification process.',
                # 'picture_original': 'Upload your picture. After uploading, please choose which part of the picture to show in "Preview" below.',
            }
            labels = {
                'centers': 'Center Affiliation',
                'phone_main': 'Primary phone',
                'phone_backup': 'Backup phone',
                'note': 'Personal note',
                # 'picture_original': 'Picture upload',
                # 'picture_cropping': 'Picture preview'
            }

    if request.method == 'POST':
        form_user = UserEditForm(request.POST, instance=user_profile.user)
        form_profile = ProfileForm(request.POST, request.FILES, instance=user_profile.profile)
        center_changed = False

        if form_user.is_valid() and form_profile.is_valid():
            if form_user.has_changed():
                form_user.save()

            if form_profile.has_changed():
                # handle role changes.
                role_new_id = form_profile.cleaned_data['role']
                if role_new_id != role_initial_id:
                    # first, remove original group.
                    try:
                        Group.objects.get(pk=role_initial_id).user_set.remove(user_profile.user)
                    except Group.DoesNotExist:
                        pass
                    # add new group if needed
                    try:
                        Group.objects.get(pk=role_new_id).user_set.add(user_profile.user)
                    except Group.DoesNotExist:
                        pass
                    # changing role requires verification again.
                    form_profile.instance.verified = None
                    Log.create(Log.SIGNUP, user_profile.user, [user_profile.user], 'role change')

                # handle centers change.
                if user_profile.get_centers_id_set() != set([c.pk for c in form_profile.cleaned_data['centers']]):
                    # changing role requires verification again.
                    form_profile.instance.verified = None
                    center_changed = True

                if not user_profile.has_profile():
                    # assign the correct user instance to create a new Profile instance.
                    form_profile.instance.user = user_profile.user

                form_profile.save()
                # log this only after profile is saved so that managers from the new center will get notified.
                if center_changed:
                    Log.create(Log.SIGNUP, user_profile.user, [user_profile.user], 'center change')

            if form_user.has_changed() or form_profile.has_changed():
                messages.success(request, 'Profile updated.')
            else:
                messages.warning(request, 'Nothing has updated.')
            return redirect('dashboard')
    else:
        form_user = UserEditForm(instance=user_profile.user)
        form_profile = ProfileForm(instance=user_profile.profile)

    return render(request, 'user/edit.html', {'user_profile': user_profile, 'form_user': form_user, 'form_profile': form_profile})


def password_reset(request):
    redirect_url = '/'
    try:
        response = auth_views.password_reset(request,
            template_name='user/password_reset.html',
            post_reset_redirect=redirect_url,
            email_template_name='user/email/password_reset_email.html',
            subject_template_name='user/email/password_reset_subject.html'
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
        template_name='user/password_reset_confirm.html', post_reset_redirect=reverse('login'))
    if isinstance(response, HttpResponseRedirect):
        messages.success(request, 'Password reset successfully. Please login using your new password.')
    return response


@login_required
def password_change(request):
    redirect_url = '/'
    response = auth_views.password_change(request,
        template_name='user/password_change.html',
        post_change_redirect=redirect_url)
    if isinstance(response, HttpResponseRedirect):
        messages.success(request, 'Your password has changed successfully.')
    return response


@login_required
@user_is_verified
@user_is_center_manager
def verify(request, *args, **kwargs):
    unverified = User.objects.filter(profile__verified__isnull=True, profile__centers__in=request.user.profile.centers.all())

    # VerifyForm is created at both GET and POST. there's no guarantee that "choices" are the same in between
    # Therefore, POST might complain "invalid" form if choices from "GET" is not in choices from "POST".
    # A solution is to use
    class VerifyForm(Form):
        users = MultipleChoiceField(label='Users to verify', choices=[(u.pk, u.get_full_name() or u.username) for u in unverified])

    class VerifyView(FormView):
        template_name = 'base_form.html'
        form_class = VerifyForm
        # success_url = reverse('user:verify')
        success_url = request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else reverse('user:verify')

        def form_valid(self, form):
            verified_list = []
            for uid in form.cleaned_data['users']:
                p = UserProfile.get_by_id(uid)
                # we only process the case when the user has a profile, which is assumed true because of center affiliation
                if not p.is_verified() and p.has_profile():
                    p.profile.verified = True
                    p.profile.save()
                    verified_list.append(p)
                    Log.create(Log.VERIFY, request.user, [p.user])
            messages.success(request, 'Successfully verified: %s' % ', '.join([p.get_full_name() or p.username for p in verified_list]))
            return super(VerifyView, self).form_valid(form)

    return VerifyView.as_view()(request, *args, **kwargs)


@login_required
def picture(request):
    user_profile = UserProfile(request.user)

    class PictureForm(ModelForm):
        class Meta:
            model = Profile
            fields = ('picture_original', 'picture_cropping')
            help_texts = {
                'picture_original': 'Upload your picture. After uploading, please choose which part of the picture to show in "Preview" below.',
            }
            labels = {
                'picture_original': 'Picture upload',
                'picture_cropping': 'Picture preview'
            }

    if request.method == 'POST':
        form = PictureForm(request.POST, request.FILES, instance=user_profile.profile)
        if form.is_valid():
            if form.has_changed():
                if not user_profile.has_profile():
                    form.instance.user = user_profile.user
                form.save()
                messages.success(request, 'Picture updated.')
            else:
                messages.warning(request, 'Nothing has updated.')
            return redirect('user:picture')
    else:
        form = PictureForm(instance=user_profile.profile)

    return render(request, 'user/picture.html', {'user_profile': user_profile, 'form': form})


@login_required
@user_is_me_or_same_center
def profile(request, uid=None):
    user_profile = UserProfile.get_by_id_default(uid, request.user)
    return render(request, 'user/profile.html', {'user_profile': user_profile})