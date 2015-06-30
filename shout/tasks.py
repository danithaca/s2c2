from django.contrib.auth.models import User
from celery import shared_task
from shout.models import Shout
from shout.notify import notify_agent


@shared_task
def shout_to_circle(shout):
    assert shout.audience == Shout.Audience.CIRCLE.value
    if not shout.delivered:
        users = User.objects.filter(membership__circle__in=shout.to_circles.all(), membership__active=True, membership__approved=True).exclude(id=shout.from_user.id).distinct()

        ctx = {
            'subject': shout.subject,
            'body': shout.body,
            'from_user': shout.from_user
        }
        notify_agent.send(shout.from_user, list(users), 'shout/messages/shout_to_circle', ctx)

        shout.delivered = True
        shout.save()
