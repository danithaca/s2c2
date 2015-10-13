from django import forms
from django.db.models import Q

from circle.models import Circle
from shout.models import Shout


class ShoutToCircleForm(forms.ModelForm):
    required_css_class = 'required'
    # to_field = forms.CharField(required=True)

    class Meta:
        model = Shout
        # fields = ['to_field', 'to_circles', 'subject', 'body']
        fields = ['to_circles', 'subject', 'body']

    def __init__(self, from_user, *args, **kwargs):
        self.from_user = from_user
        super().__init__(*args, **kwargs)
        self.fields['to_circles'].queryset = Circle.objects.filter(Q(owner=from_user, type=Circle.Type.PERSONAL.value) | Q(type=Circle.Type.PUBLIC.value, membership__member=from_user, membership__active=True, membership__approved=True)).distinct()

    # def clean(self):
    #     cleaned_data = super().clean()
    #     to_field = cleaned_data.get('to_field', '')
    #     circles = []
    #     for circle_id in (s.strip() for s in re.split(r'[\s,;]+', to_field)):
    #         try:
    #             circle = Circle.objects.get(id=circle_id)
    #             if circle.owner == self.from_user or self.from_user in circle.membership_set.all():
    #                 circles.append(circle)
    #         except:
    #             pass
    #
    #     if circles:
    #         cleaned_data['to_circles'] = circles
    #     else:
    #         raise forms.ValidationError('Found no valid circles to shout to.')
    #     return cleaned_data


class ShoutMessageOnlyForm(forms.ModelForm):
    class Meta:
        model = Shout
        fields = ['body']
        labels = {
            'body': ''      # 'Message'
        }
        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Please type your message here. We appreciate your feedback!', 'rows': 4})
        }


class ShoutToUserForm(forms.ModelForm):
    class Meta:
        model = Shout
        # fields = ['body', 'from_user', 'to_users']
        fields = ['body']
        labels = {
            'body': ''      # 'Message'
        }
        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Type your message here.', 'rows': 4}),
            # if those are "HiddenInput", then Form cannot parse correctly.
            # using CSS hidden would work, but too many users will clutter performance
            # 'from_user': forms.HiddenInput(),
            # 'to_users': forms.HiddenInput(),
        }