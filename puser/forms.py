import account.views
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, fields_for_model
from puser.models import Info


class SignupBasicForm(account.views.SignupForm):
    required_css_class = 'required'

    area = fields_for_model(Info, fields=['area'])['area']

    def __init__(self, *args, **kwargs):
        super(SignupBasicForm, self).__init__(*args, **kwargs)
        # this is suggested from the documentation
        del self.fields["username"]
        # this is "OrderedDict
        self.fields.move_to_end('email', False)


class UserInfoForm(ModelForm):
    required_css_class = 'required'
    first_name = fields_for_model(User, fields=['first_name'])['first_name']
    last_name = fields_for_model(User, fields=['last_name'])['last_name']

    class Meta:
        model = Info
        fields = ['first_name', 'last_name', 'phone', 'address', 'area', 'note', 'picture_original', 'picture_cropping']
        # fields = ['first_name', 'last_name', 'phone', 'address', 'note']
        labels = {
            'note': 'About me',
        }


class SignupConfirmForm(forms.Form):
    confirm = forms.BooleanField(widget=forms.HiddenInput, initial=True)