import re

from django import forms

from circle.models import Circle, Membership
from p2.utils import is_valid_email
from puser.models import PUser


class EmailListForm(forms.Form):
    favorite = forms.CharField(label='Contacts', widget=forms.HiddenInput, required=False, help_text='One email per line.')
    # if force_save, then save in form_valid() regardless of whether the form has changed or not.
    force_save = forms.BooleanField(widget=forms.HiddenInput, initial=False, required=False)
    send = forms.BooleanField(initial=True, required=False, label='Notify newly added contacts')

    def __init__(self, *args, **kwargs):
        self.full_access = kwargs.pop('full_access', None)
        super().__init__(*args, **kwargs)
        if self.full_access is False:
            self.fields['send'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        favorite = cleaned_data.get('favorite')
        cleaned_data['favorite_list'] = [e.strip() for e in re.split(r'[\s,;]+', favorite) if is_valid_email(e.strip())]
        # we don't validate for now
        # raise forms.ValidationError('')
        return cleaned_data

    def get_favorite_email_list(self):
        l = list(set(self.cleaned_data['favorite_list']))
        assert isinstance(l, list), 'Call only after cleaned form.'
        return l


class CircleCreateForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Circle
        fields = ['name', 'description', 'homepage']
        labels = {
            'homepage': 'Web page'
        }
        help_texts = {
            'homepage': 'Optional. E.g., the group\'s Facebook page.'
        }
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'What is this group?', 'rows': 3}),
            'homepage': forms.TextInput(attrs={'placeholder': 'http://'}),
        }


# update user connection from initiate_user to target_user.
class UserConnectionForm(forms.Form):
    # initiate_user = forms.ModelChoiceField(queryset=PUser.objects.all())
    # target_user = forms.ModelChoiceField(queryset=PUser.objects.all())
    parent_circle = forms.BooleanField(required=False, label='Connect as parent')
    sitter_circle = forms.BooleanField(required=False, label='Connect as paid babysitter')

    def __init__(self, initiate_user=None, target_user=None, *args, **kwargs):
        assert initiate_user is not None and target_user is not None
        super().__init__(*args, **kwargs)
        area = initiate_user.get_area()
        self.initial['parent_circle'] = Membership.objects.filter(member=target_user, circle__owner=initiate_user, circle__type=Circle.Type.PARENT.value, circle__area=area, active=True, approved=True).exists()
        self.initial['sitter_circle'] = Membership.objects.filter(member=target_user, circle__owner=initiate_user, circle__type=Circle.Type.SITTER.value, circle__area=area, active=True, approved=True).exists()


class MembershipCreateForm(forms.ModelForm):
    introduce = forms.BooleanField(required=False, label='Ask for an introduction from shared social connections?', help_text='Check this box to allow Servuno email your shared connections with the person for an introduction.')
    is_sitter = forms.BooleanField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Membership
        # the rest of the field is handled by View
        fields = ['note']
        # labels = {
        #     'note': 'Affiliation',
        # }
        widgets = {
            'note': forms.Textarea(attrs={'placeholder': 'Type in here ...', 'rows': 3}),
        }
        # help_texts = {
        #     'note': 'What is your affiliation to the group? E.g., Jack\'s mon.'
        # }


class MembershipEditForm(forms.ModelForm):
    # redirect = forms.CharField(required=False, widget=forms.HiddenInput)

    # def __init__(self, *args, **kwargs):
    #     choices = kwargs.pop('choices', None)
    #     if choices:
    #         self.fields['type'].choices = choices
    #     help_message = kwargs.pop('help')

    class Meta:
        model = Membership
        fields = ['note', 'as_admin']
        labels = {
            'note': 'Note',
            'as_admin': 'Mark as admin'
        }
        widgets = {
            # 'type': forms.HiddenInput(),
            'note': forms.Textarea(attrs={'placeholder': 'Leave an optional note.', 'rows': 3}),
        }

    # def __init__(self, circle=None, member=None, active=None, approved=None, type=None, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if circle is not None:
    #         self.fields['circle'].initial = circle
    #         self.fields['circle'].widget = forms.HiddenInput()
    #     if member is not None:
    #         self.fields['member'].initial = member
    #         self.fields['member'].widget = forms.HiddenInput()
    #     if active is not None:
    #         self.fields['active'].initial = active
    #         self.fields['active'].widget = forms.HiddenInput()
    #     if approved is not None:
    #         self.fields['approved'].initial = approved
    #         self.fields['approved'].widget = forms.HiddenInput()
    #     if type is not None:
    #         self.fields['type'].initial = type
    #         self.fields['type'].widget = forms.HiddenInput()


# class MembershipActivationForm(forms.ModelForm):
#     redirect = forms.CharField(required=False, widget=forms.HiddenInput)
#
#     class Meta:
#         model = Membership
#         fields = ['active']
#         widgets = {
#             'active': forms.HiddenInput(),
#         }