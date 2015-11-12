from celery import shared_task
from django.core.urlresolvers import reverse

from puser.models import PUser


@shared_task
def handle_public_membership_approval(membership):
    assert membership.circle.is_type_public() and membership.active
    if not membership.approved:
        # todo: do the real work with voucher
        # right now, send to site admin.
        link = '/admin/circle/membership/%d/' % membership.id
        from shout.notify import notify_agent
        notify_agent.send(None, None, 'circle/messages/public_membership_approval', {
            'approval_link': link,
            'applicant': membership.member,
            'applicant_link': PUser.from_user(membership.member).get_absolute_url(),
            'circle': membership.circle,
            'membership': membership
        })


@shared_task
def circle_send_invitation(circle, target_user, send_user):
    """
    This is the hub that sends out invitation to users (new or existing) when they are added to a circle.
    """
    target_user = target_user.to_puser()
    from shout.notify import notify_agent
    #link = reverse('circle:parent')

    context = {
        # 'review_link': link,
        'circle': circle,
        'target_user': target_user
    }
    if not target_user.is_registered():
        context['signup_warning'] = True

    if send_user is None:
        send_user = circle.owner

    if circle.is_type_parent():
        notify_agent.send(send_user, target_user, 'circle/messages/parent_added', context)
    elif circle.is_type_sitter():
        notify_agent.send(send_user, target_user, 'circle/messages/sitter_added', context)
    elif circle.is_type_tag():
        notify_agent.send(send_user, target_user, 'circle/messages/group_invited', context)
