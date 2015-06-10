from django import forms


class SignupFavoriteForm(forms.Form):
    favorite_list = forms.CharField(label='Favorite', widget=forms.Textarea)


class SignupCircleForm(forms.Form):
    circle_list = forms.CharField(label='Circle', widget=forms.Textarea)