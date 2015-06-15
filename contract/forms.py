from datetimewidget.widgets import DateTimeWidget
from django import forms
from contract.models import Contract


class ContractForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Contract
        fields = ['event_start', 'event_end', 'price', 'description', 'area']
        w = DateTimeWidget(bootstrap_version=3, options={
            'format': 'yyyy-mm-dd hh:ii:ss',
            'minuteStep': 15,
            'showMeridian': True,
        })
        widgets = {
            'event_start': w,
            'event_end': w
        }