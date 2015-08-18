import account.views
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, fields_for_model
from puser.models import Info


class SignupBasicForm(account.views.SignupForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # todo: think about whether to require these 2 fields.
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta:
        model = Info
        fields = ['area', 'first_name', 'last_name', 'phone', 'address', 'note']
        # fields = ['first_name', 'last_name', 'phone', 'address', 'note']
        labels = {
            'area': 'Activity area',
            'note': 'About me',
        }
        help_texts = {
            'area': 'This is where most of the babysitting activities take place.',
            'phone': 'This number will be shown to people your trust.',
            'address': 'This will help people find you for babysitting activities.',
            'note': 'Tell people a little bit about yourself.'
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
            'picture_cropping': 'Drag to choose which part of the picture to use as your avatar.',
        }
        labels = {
            'picture_original': 'Picture upload',
            'picture_cropping': 'Picture preview'
        }