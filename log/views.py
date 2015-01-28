from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.generic import ListView
from log.models import Notification
from s2c2.utils import get_now


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

    return NotificationView.as_view(user=request.user)(request)