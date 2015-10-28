from datetime import datetime, timedelta
from decimal import Decimal

from braces.views import JSONResponseMixin, AjaxResponseMixin, LoginRequiredMixin, FormValidMessageMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.core.validators import MinValueValidator
from django.db.models import Q
from django.views.generic import CreateView, DetailView, ListView, View, TemplateView, UpdateView
from django.utils import timezone

from django.template.loader import render_to_string
from django.conf import settings

from contract.forms import ContractForm
from contract.models import Contract, Match, Engagement


class ContractDetail(LoginRequiredMixin, DetailView):
    model = Contract
    template_name = 'contract/contract_view/full.html'

    def get_context_data(self, **kwargs):
        contract = self.object
        ctx = super().get_context_data(**kwargs)
        # ctx['matches'] = self.object.match_set.all().order_by('-score')
        tabs = []
        for status in (Match.Status.ACCEPTED, Match.Status.ENGAGED, Match.Status.DECLINED, Match.Status.INITIALIZED):
            qs = contract.match_set.filter(status=status.value).order_by('-score')
            if qs.exists():
                status_label = None
                matches = []
                for match in qs:
                    if status_label is None:
                        status_label = match.display_status()['label']
                    elif status_label != match.display_status()['label']:
                        status_label = status.name.capitalize()
                    matches.append(match)
                tabs.append((status_label, matches))
        if tabs:
            ctx['matches_tabs'] = tabs

        # if self.request.puser.id == contract.initiate_user.id and self.request.puser.is_isolated():
        #     messages.warning(self.request, 'You have few contacts on Servuno. Please <a href="%s">add other parents</a> and/or <a href="%s">add paid babysitters</a>.' % (reverse_lazy('circle:parent'), reverse_lazy('circle:sitter')), extra_tags='safe')

        return ctx


class ContractList(ListView):
    model = Contract
    template_name = 'contract/list.html'
    ordering = '-updated'


class ContractUpdateMixin(object):
    model = Contract
    form_class = ContractForm
    template_name = 'contract/contract_edit/edit.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['client'] = self.request.puser
        return kwargs


class ContractCreate(LoginRequiredMixin, FormValidMessageMixin, ContractUpdateMixin, CreateView):
    form_valid_message = 'Request successfully created.'

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
        # current user's location is the default location for the contract.
        initial['area'] = self.request.puser.get_area()
        # process start/end
        for token in ('start', 'end'):
            token_value =  self.request.GET.get(token, None)
            if token_value:
                initial['event_' + token] = token_value
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['client'] = self.request.puser
        return ctx

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     if self.request.puser.is_isolated():
    #         messages.warning(self.request, 'You have few contacts on Servuno. Please <a href="%s">add more contacts</a> and/or <a href="%s">join more parents circles</a>.' % (reverse_lazy('circle:manage_personal'), reverse_lazy('circle:manage_public')), extra_tags='safe')
    #     # form.fields['area'].widget.attrs['disabled'] = True
    #     return form

    def alter_contract(self, contract):
        pass

    def form_valid(self, form):
        contract = form.instance
        contract.initiate_user = self.request.puser
        contract.status = Contract.Status.INITIATED.value
        self.alter_contract(contract)
        return super().form_valid(form)

# this is hard to implement because the preview doesn't handle cbv well, unless perhaps use mixins.
# class ContractCreatePreview(FormPreview, ContractCreate):
#     form_template = 'contract/contract_update.html'
#
#     def get_initial(self):
#         initial = super().get_initial()
#         return initial
#
#     def done(self, request, cleaned_data):
#         pass


class ContractCreateParentView(ContractCreate):
    template_name = 'contract/contract_edit/create_parent.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['price'] = 0
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_target'] = True
        return context


class ContractCreateSitterView(ContractCreate):
    template_name = 'contract/contract_edit/create_sitter.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['price'] = 10
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['show_price'] = True
        return ctx


class ContractCreateOfferView(ContractCreateParentView):
    template_name = 'contract/contract_edit/create_offer.html'

    def alter_contract(self, contract):
        contract.reversed = True


class ContractEdit(LoginRequiredMixin, FormValidMessageMixin, ContractUpdateMixin, UpdateView):
    form_valid_message = 'Job post successfully updated.'
    template_name = 'contract/contract_edit/edit.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # if not form.is_bound:
        #     messages.warning(self.request, 'You CANNOT change the date/time or reduce payment. To do so, cancel the request and create a new one.')
        # todo: double check security issue
        form.fields['event_start'].widget.attrs['readonly'] = True
        form.fields['event_end'].widget.attrs['readonly'] = True
        # form.fields['price'].widget.attrs['readonly'] = True
        form.fields['price'].min_value = self.object.price
        form.fields['price'].validators.append(MinValueValidator(self.object.price))
        # form.base_price = self.object.price
        return form

    def get_initial(self):
        initial = super().get_initial()
        contract = self.object
        if contract.audience_type == Contract.AudienceType.SMART.value:
            initial['audience'] = 0
        elif contract.audience_type == Contract.AudienceType.CIRCLE.value:
            initial['audience'] = contract.parse_audience_data()
        return initial

    def form_valid(self, form):
        result = super().form_valid(form)
        if form.has_changed():
            from contract.tasks import after_contract_updated
            after_contract_updated.delay(form.instance)
        return result

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['show_price'] = True
        return ctx


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
            assert False, 'Operation not recognized: "%s"' % op
        return self.render_json_response({'success': True, 'op': op})


class MatchDetail(LoginRequiredMixin, DetailView):
    model = Match
    template_name = 'contract/match_view/full.html'
    # edit = False

    def get_context_data(self, **kwargs):
        match = self.object
        kwargs['contract'] = match.contract
        kwargs['favors_karma'] = match.count_favors_karma()
        if kwargs['favors_karma'] < 0 and not match.is_responded():
            messages.info(self.request, 'You owe %s a favor. Please consider return the favor by accepting the request.' % match.contract.initiate_user.get_name())
        # kwargs['edit'] = self.edit
        return super().get_context_data(**kwargs)


class MatchStatusChange(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, View):
    # in urls.py, "switch" controls whether to do accept or do decline.
    switch = None

    def post_ajax(self, request, pk):
        match = Match.objects.get(pk=pk)
        response = request.POST.get('response', None)
        if response is not None:
            match.response = response
            match.save()
        if self.switch is True and not match.is_accepted():
            match.accept()
        elif self.switch is False and not match.is_declined():
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
        get_date = lambda s: timezone.make_aware(datetime.strptime(s, '%Y-%m-%d'))
        to_date = lambda d: timezone.localtime(d).isoformat()
        puser = request.puser
        start, end = request.GET.get('start', None), request.GET.get('end', None)
        if start and end:
            start, end = get_date(start), get_date(end)
        else:
            start, end = timezone.now(), (timezone.now() + timedelta(days=30))

        event_list = []
        all_day = set([])
        for contract in puser.engagement_queryset().filter(Q(event_start__range=(start, end)) | Q(event_end__range=(start, end))).exclude(status=Contract.Status.CANCELED.value).distinct():
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
                'color': settings.BOOTSTRAP_COLOR_MAPPING.get(status['color'], 'gray'),
                'url': engagement.get_link(),
                'fc-header-class': '.fc-%s' % timezone.localtime(engagement.contract.event_start).strftime('%a').lower()
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


class ContractPreviewQuery(LoginRequiredMixin, JSONResponseMixin, AjaxResponseMixin, View):
    def get_ajax(self, request, *args, **kwargs):
        result = {'success': False}
        l = lambda v: Contract.parse_event_datetime_str(v)
        start, end, price = l(request.GET.get('start', None)), l(request.GET.get('end', None)), request.GET.get('price', None)
        if start and end and price:
            price = Decimal(price)
            dummy_contract = Contract(event_start=start, event_end=end, price=price)
            try:
                result['length'] = dummy_contract.display_event_length()
                result['rate'] = dummy_contract.hourly_rate()
                result['success'] = True
            except BaseException as e:
                # catch everything. fail silently
                result['message'] = str(e)
        return self.render_json_response(result)


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'contract/calendar.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # assume this is only valid for current user
        puser = self.request.puser
        engagement_list = sorted(puser.engagement_list(lambda qs: qs.filter(initiate_user=puser).order_by('-updated')[:5]) + puser.engagement_list(lambda qs: qs.filter(match__target_user=puser).order_by('-match__updated')[:5]), key=lambda e: e.updated(), reverse=True)
        ctx['engagement_recent'] = engagement_list[:5]
        return ctx
