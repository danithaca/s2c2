from braces.views import JSONResponseMixin, AjaxResponseMixin, LoginRequiredMixin
from django.forms import modelform_factory
from django.shortcuts import render
from django.views.generic import CreateView, DetailView, ListView, View
from contract.forms import ContractForm
from contract.models import Contract, Match
from datetimewidget.widgets import DateTimeWidget


class ContractDetail(DetailView):
    model = Contract
    template_name = 'contract/view.html'

    def get_context_data(self, **kwargs):
        kwargs['matches'] = self.object.match_set.all().order_by('-score')
        return super(ContractDetail, self).get_context_data(**kwargs)


class ContractList(ListView):
    model = Contract
    template_name = 'contract/list.html'
    ordering = '-updated'


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


class ContractChangeStatus(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, View):
    def post_ajax(self, request, pk):
        contract = Contract.objects.get(pk=pk)
        op = request.POST['op']
        if op == 'confirm':
            match = Match.objects.get(pk=(request.POST['match_id']))
            contract.confirm(match)
        elif op == 'cancel':
            contract.cancel()
        elif op == 'revert':
            contract.revert()
        return self.render_json_response({'success': True, 'op': op})


class MatchDetail(DetailView):
    model = Match
    template_name = 'contract/match_view.html'

    def get_context_data(self, **kwargs):
        kwargs['contract'] = self.object.contract
        return super().get_context_data(**kwargs)


class MatchStatusChange(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, View):
    switch = None

    def post_ajax(self, request, pk):
        match = Match.objects.get(pk=pk)
        if self.switch is True:
            match.accept()
        elif self.switch is False:
            match.decline()
        return self.render_json_response({'success': True})
