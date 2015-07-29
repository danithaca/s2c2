from collections import defaultdict
from datetime import datetime, timedelta
from braces.views import JSONResponseMixin, AjaxResponseMixin, LoginRequiredMixin
from django.db.models import Q
from django.forms import modelform_factory
from django.shortcuts import render
from django.views.generic import CreateView, DetailView, ListView, View, TemplateView
from contract.forms import ContractForm
from contract.models import Contract, Match, Engagement
from datetimewidget.widgets import DateTimeWidget
from django.utils import timezone
from django.template.loader import get_template, render_to_string
from django.conf import settings


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
    template_name = 'contract/add.html'

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

    def get_initial(self):
        initial = super().get_initial()
        # process area code.
        from location.models import Area
        initial['area'] = Area.default()
        # process start/end
        for token in ('start', 'end'):
            token_value =  self.request.GET.get(token, None)
            if token_value:
                initial['event_' + token] = token_value
        return initial

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     form.fields['area'].widget.attrs['disabled'] = True
    #     return form

    def form_valid(self, form):
        contract = form.instance
        contract.initiate_user = self.request.puser
        contract.status = Contract.Status.INITIATED.value
        return super().form_valid(form)


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
        elif op == 'succeed':
            contract.succeed()
        elif op == 'fail':
            contract.fail()
        else:
            assert False
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


class EngagementList(LoginRequiredMixin, TemplateView):
    template_name = 'contract/engagement_list.html'

    def get_context_data(self, **kwargs):
        user = self.request.puser
        list_engagement = []
        for contract in Contract.objects.filter(Q(initiate_user=user) | Q(match__target_user=user)).distinct().order_by('-event_start'):
            if contract.initiate_user == user:
                list_engagement.append(Engagement.from_contract(contract))
            else:
                match = Match.objects.get(contract=contract, target_user=user)
                list_engagement.append(Engagement.from_match(match))

        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'user': user,
            'engagements': list_engagement,
        })
        return ctx


# note: this is not through REST_FRAMEWORK, therefore cannot use browser to view results.
class APIMyEngagementList(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, View):

    def get_ajax(self, request, *args, **kwargs):
        # super().get_ajax(request, *args, **kwargs)      # might not be needed.
        get_date = lambda s: datetime.strptime(s, '%Y-%m-%d').date()
        to_date = lambda d: timezone.localtime(d).isoformat()
        puser = request.puser
        start, end = request.GET.get('start', None), request.GET.get('end', None)
        if start and end:
            start, end = get_date(start), get_date(end)
        else:
            start, end = timezone.now().date(), (timezone.now() + timedelta(days=30)).date()

        event_list = []
        all_day = set([])
        for contract in puser.engagement_queryset().filter(Q(event_start__range=(start, end)) | Q(event_end__range=(start, end))).distinct():
            if contract.initiate_user == puser:
                engagement = Engagement.from_contract(contract)
            else:
                try:
                    match = Match.objects.get(contract=contract, target_user=puser)
                except:
                    continue
                engagement = Engagement.from_match(match)
            status = engagement.display_status()
            # if engagement.target_user:
            #     title = '%s <-> %s (%s)' % (engagement.initiate_user.get_name(), engagement.target_user.get_name(), status.label)
            # else:
            #     title = '%s (%s)' % (engagement.initiate_user.get_name(), status['label'])
            title_icon = render_to_string('elements/icon_find.html') if engagement.is_main_contract() else render_to_string('elements/icon_serve.html')
            title_label = engagement.passive_user().get_name() if engagement.passive_user() else ''
            title = '%s: %s' % (title_icon, title_label)
            event = {
                'start': to_date(engagement.contract.event_start),
                'end': to_date(engagement.contract.event_end),
                'id': engagement.get_id(),
                'title': title,
                'color': settings.bootstrap_color_mapping.get(status['color'], 'gray'),
                'url': engagement.get_link(),
            }
            event_list.append(event)
            all_day.add(timezone.localtime(engagement.contract.event_start).date())
            all_day.add(timezone.localtime(engagement.contract.event_end).date())

        # for now, we don't show "allDay" event. the "headline" will do the trick.
        # also disabled allDay event in fullcalendar options. need to turn it on to display the allDay events.

        # for d in all_day:
        #     event_list.append({
        #         'allDay': True,
        #         'start': d.isoformat(),
        #         'end': d.isoformat(),
        #         'title': '<i class="fa fa-exclamation-circle"></i>',
        #         'color': self.color_mapping['danger'],
        #     })

        return self.render_json_response(event_list)
        #return self.get(request, *args, **kwargs)