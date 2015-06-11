from django import forms
import re
from s2c2.utils import is_valid_email


class SignupFavoriteForm(forms.Form):
    favorite = forms.CharField(label='Favorite', widget=forms.Textarea, required=False, help_text='One email per line.')

    def clean(self):
        cleaned_data = super(SignupFavoriteForm, self).clean()
        favorite = cleaned_data.get('favorite')
        cleaned_data['favorite_list'] = [e.strip() for e in re.split(r'[\s,;]+', favorite) if is_valid_email(e.strip(''))]
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
    #
    # def __init__(self, *args, **kwargs):
    #     super(SignupCircleForm, self).__init__(*args, **kwargs)
    #     self.fields['check1'] = forms.BooleanField(required=False, label='aaa')
    #     self.fields['check2'] = forms.BooleanField(required=False, label='bbb')

    circle = forms.CharField(label='Circle', widget=forms.Textarea, required=False, help_text='Separate the circle ID by commas.')