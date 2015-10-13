import json
import re

from django import forms

from circle.models import Circle, SupersetRel, Membership
from puser.models import Area, PUser
from p2.templatetags.p2_tags import p2_tag_user_full_name
from p2.utils import is_valid_email, get_int


class EmailListForm(forms.Form):
    favorite = forms.CharField(label='Contacts', widget=forms.HiddenInput, required=False, help_text='One email per line.')
    # if force_save, then save in form_valid() regardless of whether the form has changed or not.
    force_save = forms.BooleanField(widget=forms.HiddenInput, initial=False, required=False)
    send = forms.BooleanField(initial=True, required=False, label='Notify newly added contacts')

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


class ManagePersonalForm(forms.Form):
    # favorite = forms.CharField(label='Favorite', widget=forms.Textarea, required=False, help_text='One email per line.')
    favorite = forms.CharField(label='Contacts', widget=forms.HiddenInput, required=False, help_text='One email per line.')
    # if force_save, then save in form_valid() regardless of whether the form has changed or not.
    force_save = forms.BooleanField(widget=forms.HiddenInput, initial=False, required=False)
    send = forms.BooleanField(initial=True, required=False, label='Notify newly added contacts')

    def clean(self):
        cleaned_data = super().clean()
        favorite = cleaned_data.get('favorite')
        cleaned_data['favorite_list'] = [e.strip() for e in re.split(r'[\s,;]+', favorite) if is_valid_email(e.strip())]
        # we don't validate for now
        # raise forms.ValidationError('')
        return cleaned_data

    def get_favorite_email_list(self):
        l = list(set(self.cleaned_data['favorite_list']))
        assert isinstance(l, list), 'Personal circle email list is not initialized. Call only after cleaned form.'
        return l


# this is duplidate code to ManagePersonalForm
class SignupFavoriteForm(forms.Form):
    favorite = forms.CharField(label='Favorite', widget=forms.Textarea, required=False, help_text='One email per line.')

    def clean(self):
        cleaned_data = super().clean()
        favorite = cleaned_data.get('favorite')
        cleaned_data['favorite_list'] = [e.strip() for e in re.split(r'[\s,;]+', favorite) if is_valid_email(e.strip())]
        # we don't validate for now
        # raise forms.ValidationError('')
        return cleaned_data


# todo: remove puser from 'init', use area instead.
class ManagePublicForm(forms.Form):
    circle = forms.CharField(widget=forms.HiddenInput, label='Circle', required=False, help_text='Separate the circle ID by commas.')

    def clean(self):
        cleaned_data = super().clean()
        circle = cleaned_data.get('circle')
        cleaned_data['circle_list'] = [int(s) for s in re.split(r'[\s,;]+', circle) if get_int(s)]
        return cleaned_data

    def get_circle_id_list(self):
        return self.cleaned_data['circle_list']

    def __init__(self, puser, membership_circle_id_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.puser = puser
        self.membership_circle_id_list = membership_circle_id_list
        self.initial['circle'] = ','.join(list(map(str, membership_circle_id_list)))

        # build circle options
        self.circle_options = self.build_circle_options(puser.get_area())

    def build_circle_options(self, area):
        options = []
        membership_circle_id_set = set(self.membership_circle_id_list)

        # for all circles with superset
        for superset in Circle.objects.filter(type=Circle.Type.SUPERSET.value, area=area):
            d = {
                'title': superset.name,
                'description': superset.description,
                'list': []
            }
            for rel in SupersetRel.objects.filter(parent=superset, child__type=Circle.Type.PUBLIC.value, child__area=area):
                c = rel.child
                cd = {
                    'title': c.name,
                    'description': c.description,
                    'id': c.pk,
                    'count': c.count(),
                }
                if c.id in membership_circle_id_set:
                    m = Membership.objects.get(circle_id=c.id, member=self.puser)
                    cd['active'] = m.active
                    cd['approved'] = m.approved
                d['list'].append(cd)
            options.append(d)

        # for other circles that don't have superset.
        leftover = {
            'title': 'Other',
            'description': 'Other parents circles you can join.',
            'list': []
        }
        for c in Circle.objects.filter(type=Circle.Type.PUBLIC.value, area=area, child__isnull=True):
            cd = {
                'title': c.name,
                'description': c.description,
                'id': c.pk,
                'count': c.count,
            }
            if c.id in membership_circle_id_set:
                m = Membership.objects.get(circle_id=c.id, member=self.puser)
                cd['active'] = m.active
                cd['approved'] = m.approved
            leftover['list'].append(cd)
        if leftover['list']:
            options.append(leftover)

        if len(options) == 1 and options[0]['title'] == 'Other':
            # if there's only "other", then don't show "other" at all.
            options[0]['title'] = ''

        return options


class ManageAgencyForm(ManagePublicForm):
    def build_circle_options(self, area):
        membership_circle_id_set = set(self.membership_circle_id_list)
        options = []
        for circle in Circle.objects.filter(type=Circle.Type.AGENCY.value, area=area):
            option = {
                'circle': circle,
                'count': circle.count(membership_type=Membership.Type.NORMAL.value)
            }
            if circle.id in membership_circle_id_set:
                membership = Membership.objects.get(circle_id=circle.id, member=self.puser)
                option['active'] = membership.active
            options.append(option)
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
            for rel in SupersetRel.objects.filter(parent=superset, child__type=Circle.Type.PUBLIC.value, child__area=area):
                d['list'].append({
                    'title': rel.child.name,
                    'description': rel.child.description,
                    'id': rel.child.pk,
                })
            options.append(d)
        return options

# this is try to use dynamic choice field. use charfield instead.
# class ManageLoopForm(forms.Form):
#     # approved = forms.MultipleChoiceField(choices=(), required=False)
#
#     def __init__(self, puser, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.puser = puser
#         # hit db once. this will be new data in form POST.
#         self.membership_list = list(self.puser.membership_queryset_loop())
#
#         self.fields['approved'] = forms.MultipleChoiceField(
#             # might include membership from the same personal in different circles (e.g., different area)
#             choices=tuple([(m.id, m.circle.owner.get_name()) for m in self.membership_list]),
#             initial=[m.id for m in self.membership_list],
#             required=False,
#         )

class ManageLoopForm(forms.Form):
    data = forms.CharField(label='Data', widget=forms.HiddenInput, required=False, help_text='JSON data for the form.')

    def __init__(self, puser, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.puser = puser
        from p2.templatetags.p2_tags import user_picture_url
        data = [{'membership_id': m.id, 'name': p2_tag_user_full_name(m.circle.owner), 'approved': m.approved, 'picture': user_picture_url(None, m.circle.owner)} for m in self.puser.membership_queryset_loop()]
        self.membership_data = data
        self.fields['data'].initial = json.dumps(data)


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
