from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.views.generic import CreateView
from shout.forms import ShoutToCircleForm
from shout.models import Shout
from shout.tasks import shout_to_circle


class ShoutToCircle(LoginRequiredMixin, CreateView):
    model = Shout
    form_class = ShoutToCircleForm
    template_name = 'shout/add.html'
    success_url = reverse_lazy('shout:add')

    def form_valid(self, form):
        shout = form.instance
        shout.audience = Shout.AudienceType.CIRCLE.value
        shout.from_user = form.from_user

        # seems no need to handle it as long as it's the same field name.
        # to_circles = form.cleaned_data['to_circles']
        # for circle in to_circles:
        #     shout.to_circles.add(circle)

        result = super().form_valid(form)
        shout_to_circle.delay(shout)
        messages.success(self.request, 'The message will be shouted to the target audience shortly.')
        return result

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        kwargs['from_user'] = user
        return kwargs