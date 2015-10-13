from braces.views import LoginRequiredMixin, FormValidMessageMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.defaults import bad_request
from django.views.generic import CreateView
from puser.models import PUser

from shout.forms import ShoutToCircleForm, ShoutMessageOnlyForm, ShoutToUserForm
from shout.models import Shout
from shout.tasks import shout_to_circle


class ShoutToCircle(LoginRequiredMixin, CreateView):
    model = Shout
    form_class = ShoutToCircleForm
    template_name = 'shout/add.html'
    success_url = reverse_lazy('shout:add')

    def form_valid(self, form):
        shout = form.instance
        shout.audience_type = Shout.AudienceType.CIRCLE.value
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


class ShoutToAdmin(CreateView):
    model = Shout
    form_class = ShoutMessageOnlyForm
    template_name = 'shout/contact_us.html'
    success_url = '/'

    def form_valid(self, form):
        shout = form.instance
        shout.audience_type = Shout.AudienceType.ADMIN.value
        if self.request.user and self.request.user.is_authenticated():
            shout.from_user = self.request.user

        # persist
        result = super().form_valid(form)
        # deliver right away
        shout.deliver()

        messages.success(self.request, 'Message sent successfully.')
        return result


class ShoutToUser(LoginRequiredMixin, FormValidMessageMixin, CreateView):
    model = Shout
    form_class = ShoutToUserForm
    template_name = 'shout/to_user.html'
    form_valid_message = 'Message sent successfully.'

    def dispatch(self, request, *args, **kwargs):
        self.from_user = self.request.puser
        uid = kwargs.get('uid', None)
        try:
            self.to_user = PUser.objects.get(pk=uid)
        except:
            self.to_user = None
        return super().dispatch(request, *args, **kwargs)

    # todo: perhaps need a "captcha" form for the not trusted user.
    def get(self, request, *args, **kwargs):
        if self.to_user is None:
            return bad_request(request)
        return super().get(request, *args, **kwargs)

    # def get_initial(self):
    #     initial = super().get_initial()
    #     initial['from_user'] = self.from_user
    #     initial['to_users'] = [self.to_user]
    #     return initial

    def form_valid(self, form):
        shout = form.instance
        shout.audience_type = Shout.AudienceType.USER.value
        shout.from_user = self.from_user
        result = super().form_valid(form)
        # m2m need to save separately
        shout.to_users = [self.to_user]
        shout.save()
        # deliver right away
        shout.deliver()
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['to_user'] = self.to_user
        return context

    def get_success_url(self):
        return reverse('account_view', kwargs={'pk': self.to_user.pk})