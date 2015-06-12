from django import forms
import re
from circle.models import Circle, Superset
from location.models import Area
from s2c2.utils import is_valid_email, get_int


class SignupFavoriteForm(forms.Form):
    favorite = forms.CharField(label='Favorite', widget=forms.Textarea, required=False, help_text='One email per line.')

    def clean(self):
        cleaned_data = super(SignupFavoriteForm, self).clean()
        favorite = cleaned_data.get('favorite')
        cleaned_data['favorite_list'] = [e.strip() for e in re.split(r'[\s,;]+', favorite) if is_valid_email(e.strip())]
        # we don't validate for now
        # raise forms.ValidationError('')
        return cleaned_data


class SignupCircleForm(forms.Form):
    # circle = forms.MultipleChoiceField(label='Circle', widget=forms.CheckboxSelectMultiple, required=False,
    #                                    choices=(
    #                                        (1, 'Field one'),
    #                                        (2, 'Field two'),
    #                                    ),
    #                                    help_text='Choose which circle to join.')

    circle = forms.CharField(label='Circle', required=False, help_text='Separate the circle ID by commas.')

    def clean(self):
        cleaned_data = super(SignupCircleForm, self).clean()
        circle = cleaned_data.get('circle')
        cleaned_data['circle_list'] = [int(s) for s in re.split(r'[\s,;]+', circle) if get_int(s)]
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(SignupCircleForm, self).__init__(*args, **kwargs)

        # build circle options
        self.circle_options = []
        area = Area.objects.get(pk=1)  # this is ann arbor
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
            self.circle_options.append(d)


class SignupConfirmForm(forms.Form):
    confirm = forms.BooleanField(widget=forms.HiddenInput, initial=True)