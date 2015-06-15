from django.forms import modelform_factory
from django.shortcuts import render
from django.views.generic import CreateView, DetailView
from contract.forms import ContractForm
from contract.models import Contract
from datetimewidget.widgets import DateTimeWidget


class ContractDetail(DetailView):
    model = Contract
    template_name = 'contract/view.html'


class ContractCreate(CreateView):
    model = Contract
    form_class = ContractForm
    # fields = ['event_start', 'event_end', 'price', 'description', 'area']
    template_name = 'contract/add.html'

    # this doesn't work with CreateView
    # class Meta:
    #     date_time_widget = DateTimeWidget(bootstrap_version=3)
    #     widgets = {
    #         'event_start': date_time_widget,
    #         'event_end': date_time_widget,
    #     }

    # override widget.
    # def get_form_class(self):
    #     # cls = super(ContractCreate, self).get_form_class()
    #     w = DateTimeWidget(bootstrap_version=3, options={
    #         'format': 'yyyy-mm-dd hh:ii:ss',
    #         'minuteStep': 15,
    #         'showMeridian': True,
    #     })
    #     return modelform_factory(self.model, fields=self.fields, widgets={
    #         'event_start': w,
    #         'event_end': w
    #     })

    def form_valid(self, form):
        contract = form.instance
        contract.buyer = self.request.puser
        contract.status = Contract.Status.INITIATED.value
        return super(ContractCreate, self).form_valid(form)
