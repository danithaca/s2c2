from datetimewidget.widgets import DateTimeWidget
from decimal import Decimal
from django import forms
from contract.models import Contract


# note: this form is highly customized in html template. this Form class doesn't control much of how it actually shows.
class ContractForm(forms.ModelForm):
    required_css_class = 'required'
    price = forms.DecimalField(min_value=0, decimal_places=2, initial=10, label='Payment', help_text='You agree to pay the server this amount after the service is done. Paying 0 means that you want the server to serve you in exchange for favors.', widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 1}))
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
            'event_start': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Start'}),
            'event_end': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'End'}),
            'area': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'placeholder': 'Optional note', 'rows': 3})
        }
        labels = {
            'description': 'Note',
        }
        localized_fields = ['event_start', 'event_end']

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

        if event_start is not None and event_end is not None and event_start >= event_end:
            raise forms.ValidationError('End time must be later than start time.')

        return cleaned_data

