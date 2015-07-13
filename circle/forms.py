import re

from django import forms

from circle.models import Circle, Superset
from location.models import Area
from s2c2.utils import is_valid_email, get_int


class ManageFavoriteForm(forms.Form):
    # favorite = forms.CharField(label='Favorite', widget=forms.Textarea, required=False, help_text='One email per line.')
    favorite = forms.CharField(label='Favorite', widget=forms.HiddenInput, required=False, help_text='One email per line.')

    def clean(self):
        cleaned_data = super(ManageFavoriteForm, self).clean()
        favorite = cleaned_data.get('favorite')
        cleaned_data['favorite_list'] = [e.strip() for e in re.split(r'[\s,;]+', favorite) if is_valid_email(e.strip())]
        # we don't validate for now
        # raise forms.ValidationError('')
        return cleaned_data

    def get_favorite_email_list(self):
        l = list(set(self.cleaned_data['favorite_list']))
        assert isinstance(l, list), 'Favorite email list is not initialized. Call only after cleaned form.'
        return l


# this is duplidate code to ManageFavoriteForm
class SignupFavoriteForm(forms.Form):
    favorite = forms.CharField(label='Favorite', widget=forms.Textarea, required=False, help_text='One email per line.')

    def clean(self):
        cleaned_data = super(SignupFavoriteForm, self).clean()
        favorite = cleaned_data.get('favorite')
        cleaned_data['favorite_list'] = [e.strip() for e in re.split(r'[\s,;]+', favorite) if is_valid_email(e.strip())]
        # we don't validate for now
        # raise forms.ValidationError('')
        return cleaned_data


# todo: remove puser from 'init', use area instead.
class ManageCircleForm(forms.Form):
    circle = forms.CharField(widget=forms.HiddenInput, label='Circle', required=False, help_text='Separate the circle ID by commas.')

    def clean(self):
        cleaned_data = super(ManageCircleForm, self).clean()
        circle = cleaned_data.get('circle')
        cleaned_data['circle_list'] = [int(s) for s in re.split(r'[\s,;]+', circle) if get_int(s)]
        return cleaned_data

    def get_circle_id_list(self):
        return self.cleaned_data['circle_list']

    def __init__(self, puser, *args, **kwargs):
        super(ManageCircleForm, self).__init__(*args, **kwargs)
        self.puser = puser

        # build circle options
        self.circle_options = self.build_circle_options(puser.get_area())

    def build_circle_options(self, area):
        options = []
        for superset in Circle.objects.filter(type=Circle.Type.SUPERSET.value, area=area):
            d = {
                'title': superset.name,
                'description': superset.description,
                'list': []
            }
            for rel in Superset.objects.filter(parent=superset, child__type=Circle.Type.PUBLIC.value, child__area=area):
                d['list'].append({
                    'title': rel.child.name,
                    'description': rel.child.description,
                    'id': rel.child.pk,
                })
            options.append(d)
        return options


# todo: this is very similar to ManageCircleForm
class SignupCircleForm(forms.Form):
    circle = forms.CharField(label='Circle', required=False, help_text='Separate the circle ID by commas.')

    def clean(self):
        cleaned_data = super(SignupCircleForm, self).clean()
        circle = cleaned_data.get('circle')
        cleaned_data['circle_list'] = [int(s) for s in re.split(r'[\s,;]+', circle) if get_int(s)]
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(SignupCircleForm, self).__init__(*args, **kwargs)

        # build circle options
        area = Area.objects.get(pk=1)  # this is ann arbor
        self.circle_options = self.build_circle_options(area)

    def build_circle_options(self, area):
        options = []
        for superset in Circle.objects.filter(type=Circle.Type.SUPERSET.value, area=area):
            d = {
                'title': superset.name,
                'description': superset.description,
                'list': []
            }
            for rel in Superset.objects.filter(parent=superset, child__type=Circle.Type.PUBLIC.value, child__area=area):
                d['list'].append({
                    'title': rel.child.name,
                    'description': rel.child.description,
                    'id': rel.child.pk,
                })
            options.append(d)
        return options

