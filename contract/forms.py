from datetimewidget.widgets import DateTimeWidget
from decimal import Decimal
from django import forms
from django.utils import timezone
from contract.models import Contract


# note: this form is highly customized in html template. this Form class doesn't control much of how it actually shows.
class ContractForm(forms.ModelForm):
    required_css_class = 'required'
    # price = forms.DecimalField(min_value=0, decimal_places=2, initial=10, label='Payment', help_text='', widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 1}))
    price = forms.DecimalField(min_value=0, decimal_places=2, label='Payment', widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 1, 'placeholder': 'Total pay'}))
    # it seems "localize" by default is True if USE_TZ (or USE_L10N?) is turned on.
    # event_start = forms.DateTimeField(localize=True)
    # event_end = forms.DateTimeField(localize=True)

    class Meta:
        model = Contract
        fields = ['event_start', 'event_end', 'price', 'area', 'description']
        # w = DateTimeWidget(bootstrap_version=3, options={
        #     'format': 'yyyy-mm-dd hh:ii',
        #     'minuteStep': 15,
        #     'showMeridian': True,
        # })
        widgets = {
            # 'event_start': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'E.g. 12/20/2014 18:00'}),
            'event_start': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Start date/time'}),
            # 'event_end': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'E.g. 12/21/2014 19:00'}),
            'event_end': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'End date/time'}),
            'area': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'placeholder': 'Optional note', 'rows': 3})
        }
        labels = {
            'event_start': 'From',
            'event_end': 'To',
            'description': '',  # hide the label
        }
        localized_fields = ['event_start', 'event_end']
        # help_texts = {
        #     'event_start': 'Start date/time',
        #     'event_end': 'End date/time',
        # }

    class Media:
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.10.3/moment.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.14.30/js/bootstrap-datetimepicker.min.js',
        )
        css = {'all': ('https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.14.30/css/bootstrap-datetimepicker.min.css',)}

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # self.fields['price'].widget.attrs['step'] = 1
    #     self.fields['area'].widget.attrs['disabled'] = True
    #
    #     # perhaps it's better to delegate to template js to add form-control to form elements.
    #     # for fn, field in self.fields.items():
    #     #     field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(ContractForm, self).clean()
        event_start = cleaned_data.get("event_start")
        event_end = cleaned_data.get("event_end")
        now = timezone.now()

        if event_start < now or event_end < now:
            raise forms.ValidationError('The date/time you specified cannot be in the past.')
        if event_start >= event_end:
            raise forms.ValidationError('End date/time must be later than start date/time.')

        # if hasattr(self, 'base_price') and not cleaned_data.get("price") >= self.base_price:
        #     raise forms.ValidationError('End date/time must be later than start date/time.')

        return cleaned_data

