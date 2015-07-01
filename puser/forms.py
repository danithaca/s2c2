import account.views
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, fields_for_model
from puser.models import Info


class SignupBasicForm(account.views.SignupForm):
    required_css_class = 'required'
    # area = fields_for_model(Info, fields=['area'])['area']

    def __init__(self, *args, **kwargs):
        super(SignupBasicForm, self).__init__(*args, **kwargs)
        # this is suggested from the documentation
        del self.fields["username"]
        # this is "OrderedDict
        self.fields.move_to_end('email', False)


class SignupConfirmForm(forms.Form):
    confirm = forms.BooleanField(widget=forms.HiddenInput, initial=True)


class UserInfoForm(ModelForm):
    required_css_class = 'required'
    first_name = fields_for_model(User, fields=['first_name'])['first_name']
    last_name = fields_for_model(User, fields=['last_name'])['last_name']

    class Meta:
        model = Info
        fields = ['area', 'first_name', 'last_name', 'phone', 'address', 'note']
        # fields = ['first_name', 'last_name', 'phone', 'address', 'note']
        labels = {
            'area': 'Activity area',
            'note': 'About me',
        }
        help_texts = {
            'area': 'This is where most of the babysitting activities you are associated take place. It does not have to agree with your address.',
            'phone': 'People in your circles will see this number and contact you with it.',
            'address': 'This will help people find you for babysitting related activities.',
            'note': 'Tell people a little bit about yourself.'
        }


class UserPictureForm(ModelForm):
    class Meta:
        model = Info
        fields = ('picture_original', 'picture_cropping')
        help_texts = {
            'picture_original': 'Upload your picture. After uploading, please choose which part of the picture to show below.',
            'picture_cropping': 'Choose which part of the picture to use as your avatar.',
        }
        labels = {
            'picture_original': 'Picture upload',
            'picture_cropping': 'Picture preview'
        }