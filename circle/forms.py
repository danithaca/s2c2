import re

from django import forms

from circle.models import Circle, Membership
from p2.utils import is_valid_email, RelationshipType
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


class MembershipCreateForm(forms.ModelForm):
    introduce = forms.BooleanField(required=False, label='I would like a shared friend to introduce me.')
    is_sitter = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        # only applies to personal circle join.
        self.target_user = kwargs.pop('target_user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Membership
        # the rest of the field is handled by View
        fields = ['as_rel', 'private_note']
        labels = {
            'as_rel': 'How do you know %s (Check all that apply)',
            'private_note': 'Additional note (optional)',
        }
        widgets = {
            'private_note': forms.Textarea(attrs={'placeholder': 'Add a private note between you and the person you are connecting with.', 'rows': 2}),
        }
        # help_texts = {
        #     'private_note': 'This note is private between you and the person you are connecting with.'
        # }

    def clean_as_rel(self):
        as_rel_val = self.data.getlist('as_rel', [])
        as_rel_db_val = RelationshipType.to_db(as_rel_val)
        return as_rel_db_val

    def clean(self):
        cleaned_data = super().clean()
        # self.data has the raw data, where as_rel is in the list form.
        # cleaned_data['as_rel'] = RelationshipType.to_db(self.data['as_rel'])
        return cleaned_data


class ParentAddForm(MembershipCreateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.target_user is not None
        self.fields['as_rel'].label = self.fields['as_rel'].label % self.target_user.get_full_name()
        self.fields['introduce'].label = 'I don\'t know %s. I would like a shared friend to introduce me.' % self.target_user.get_full_name()
        rel_choices = [
            (RelationshipType.NEIGHBOR.value, 'We are neighbors'),
            (RelationshipType.EXTENDED_FAMILY.value, 'We are family'),
            (RelationshipType.FRIEND.value, 'We are friends'),
            (RelationshipType.COLLEAGUE.value, 'We work together'),
            (RelationshipType.KID_FRIEND.value, 'Our kids go to school together'),
        ]
        self.fields['as_rel'].widget = forms.CheckboxSelectMultiple(choices=rel_choices)


class SitterAddForm(forms.ModelForm):
    is_sitter = forms.BooleanField(required=False, widget=forms.HiddenInput, initial=True)
    introduce = forms.BooleanField(required=False, label='I would like a shared friend to introduce me.')

    class Meta:
        model = Membership
        fields = ['private_note']
        labels = {
            'private_note': 'Private Note',
        }
        widgets = {
            'private_note': forms.Textarea(attrs={'placeholder': 'This private note is visible only between you and the person you are connecting with.', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.target_user = kwargs.pop('target_user', None)
        super().__init__(*args, **kwargs)
        assert self.target_user is not None
        self.fields['introduce'].label = 'I don\'t know %s. I would like a shared friend to introduce me.' % self.target_user.get_full_name()


class MembershipEditForm(forms.ModelForm):

    class Meta:
        model = Membership
        fields = ['note', 'as_admin']
        # fields = ['note', 'as_admin', 'approved']
        labels = {
            'note': 'Note',
            'as_admin': 'Mark as admin'
        }
        widgets = {
            # 'type': forms.HiddenInput(),
            'note': forms.Textarea(attrs={'placeholder': 'Leave an optional note.', 'rows': 3}),
            # 'approved': forms.HiddenInput(),
        }
