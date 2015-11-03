from account.forms import LoginEmailForm
import account.views
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, fields_for_model

from puser.models import Info, PUser, Waiting


class SignupBasicForm(account.views.SignupForm):
    # required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # this is suggested from the documentation
        del self.fields["username"]
        # this is "OrderedDict
        self.fields.move_to_end('email', False)

    # here we override to allow existing email if the email is "pre-registered".
    def clean_email(self):
        value = self.cleaned_data["email"]
        try:
            user = PUser.get_by_email(value)
            if not user.is_registered():
                self.cleaned_data['pre_registered_user'] = user
                return
        except PUser.DoesNotExist:
            pass
        return super().clean_email()


class SignupFullForm(ModelForm, account.views.SignupForm):
    required_css_class = 'required'
    area = fields_for_model(Info, fields=['area'])['area']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # this is suggested from the documentation
        del self.fields["username"]
        # this is "OrderedDict
        self.fields.move_to_end('email', False)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['area'].label = 'Activity area'
        self.fields['area'].help_text = 'This is where most of the babysitting activities take place.'

    # here we override to allow existing email if the email is "pre-registered".
    def clean_email(self):
        value = self.cleaned_data["email"]
        try:
            user = PUser.get_by_email(value)
            if not user.is_registered():
                self.cleaned_data['pre_registered_user'] = user
                return
        except PUser.DoesNotExist:
            pass
        return super().clean_email()

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 'area']


class WaitingForm(forms.Form):
    required_css_class = 'required'
    email = fields_for_model(Waiting, fields=['email'])['email']
    invitation_code = forms.CharField(required=False, max_length=64, help_text='If you have an invitation code, please type in here.')


class SignupConfirmForm(forms.Form):
    confirm = forms.BooleanField(widget=forms.HiddenInput, initial=True)


class UserInfoForm(ModelForm):
    required_css_class = 'required'
    first_name = fields_for_model(User, fields=['first_name'])['first_name']
    last_name = fields_for_model(User, fields=['last_name'])['last_name']
    email = fields_for_model(User, fields=['email'])['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # todo: think about whether to require these 2 fields.
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['email'].label = 'Email'
        self.fields['email'].widget.attrs['readonly'] = True

    class Meta:
        model = Info
        fields = ['first_name', 'last_name', 'area', 'email', 'phone', 'address', 'note']
        # fields = ['first_name', 'last_name', 'phone', 'address', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3})
        }
        labels = {
            'area': 'Activity area',
            'note': 'About me',
            'phone': 'Phone number',
        }
        help_texts = {
            'area': 'This is where most of the babysitting activities take place. Limited to Ann Arbor and Ypsilanti at the time being.',
            # 'phone': 'This number will be shown to people your trust.',
            'address': 'This helps your contacts find you for babysitting activities.',
            'note': 'Tell people a little bit about yourself and the kids to be taken care of.'
        }


class UserInfoOnboardForm(ModelForm):
    required_css_class = 'required'
    first_name = fields_for_model(User, fields=['first_name'])['first_name']
    last_name = fields_for_model(User, fields=['last_name'])['last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta:
        model = Info
        fields = ['first_name', 'last_name', 'area']
        labels = {
            'area': 'Activity area',
        }
        help_texts = {
            'area': 'This is where most of the babysitting activities take place. Limited to Ann Arbor and Ypsilanti at the time being.',
        }


class UserPictureForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.picture_original:
            # self.fields['picture_cropping'].help_text = 'N/A. Please upload picture first.'
            self.fields['picture_original'].help_text = ''
            del self.fields['picture_cropping']

    class Meta:
        model = Info
        fields = ('picture_original', 'picture_cropping')
        help_texts = {
            # 'picture_original': 'Please choose which part of the picture to show.',
            'picture_cropping': 'Select which part of the picture to use as your avatar.',
        }
        labels = {
            'picture_original': 'Picture upload',
            'picture_cropping': 'Picture preview'
        }


class LoginEmailAdvForm(LoginEmailForm):
    authentication_fail_message = "The email address and/or password you specified are not correct."
