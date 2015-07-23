from datetimewidget.widgets import DateTimeWidget
from django import forms
from contract.models import Contract


class ContractForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Contract
        fields = ['event_start', 'event_end', 'price', 'area', 'description']
        w = DateTimeWidget(bootstrap_version=3, options={
            'format': 'yyyy-mm-dd hh:ii',
            'minuteStep': 15,
            'showMeridian': True,
        })
        widgets = {
            'event_start': w,
            'event_end': w,
        }

    def clean(self):
        cleaned_data = super(ContractForm, self).clean()
        event_start = cleaned_data.get("event_start")
        event_end = cleaned_data.get("event_end")

        if event_start is not None and event_end is not None and event_start >= event_end:
            raise forms.ValidationError('End time must be later than start time.')

        return cleaned_data

