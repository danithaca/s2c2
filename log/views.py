from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, FormView
from django_ajax.mixin import AJAXMixin
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from location.models import Location
from log.models import Notification, Log
from log.serializers import LogSerializer
from s2c2.utils import get_now, get_request_day
from slot.models import DayToken


@login_required
def notification(request):

    class NotificationView(ListView):
        template_name = 'notification.html'
        context_object_name = 'latest_notification'
        # see http://stackoverflow.com/questions/11494483/django-class-based-view-how-do-i-pass-additional-parameters-to-the-as-view-meth
        user = None

        def get_queryset(self):
            q = Q(done=False) | Q(created__day=get_now().day)
            return Notification.objects.filter(q, receiver=self.user).order_by('-created')

        def get_context_data(self, **kwargs):
            form = MarkReadForm()
            form.fields['unread'].widget = forms.HiddenInput()
            form.fields['unread'].initial = ','.join([str(i) for i in self.get_queryset().values_list('pk', flat=True)])
            kwargs['form'] = form
            return super(NotificationView, self).get_context_data(**kwargs)

    return NotificationView.as_view(user=request.user)(request)


class MarkReadForm(forms.Form):
    # this should be a list of notification id separated by ','
    unread = forms.CharField()


class MarkRead(AJAXMixin, FormView):
    ajax_mandatory = False
    form_class = MarkReadForm
    template_name = 'base_form.html'

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', reverse('log:mark_read'))

    def form_valid(self, form):
        unread_list = form.cleaned_data['unread'].split(',')
        Notification.objects.filter(pk__in=unread_list).update(done=True)
        return super(MarkRead, self).form_valid(form)


class CommentByLocation(generics.ListCreateAPIView):
    serializer_class = LogSerializer
    # model = Log

    def get_queryset(self):
        day = get_request_day(self.request)
        ref = '%s,%s' % (self.kwargs['cid'], day.get_token())
        return Log.objects.filter(type=Log.COMMENT_BY_LOCATION, ref=ref)

    # def post(self, request, *args, **kwargs):
    #     return super(CommentByLocation, self).post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = {
            'message': request.data['message'],
            'type': Log.COMMENT_BY_LOCATION,
            'creator': request.user.id,
            'ref': '%s,%s' % (kwargs['cid'], request.data['day'])
        }
        serializer = self.get_serializer(data=data)

        # start copy from super.
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # def create(self, request, *args, **kwargs):
    #     location = get_object_or_404(Location, pk=self.kwargs['cid'])
    #     Log.create_comment_by_location(request.user, location, DayToken.from_token(request.data['day']), request.data['message'])
    #     return JsonResponse({'success': True})


class CommentByLocationDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Log.objects.filter(type=Log.COMMENT_BY_LOCATION)
    serializer_class = LogSerializer