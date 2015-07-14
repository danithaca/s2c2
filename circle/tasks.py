from celery import shared_task
from puser.models import PUser


@shared_task
def handle_publich_membership_approval(membership):
    assert membership.circle.is_type_public() and membership.active
    if not membership.approved:
        # todo: do the real work with voucher
        # right now, send to site admin.
        link = '/admin/circle/membership/%d/' % membership.id
        from shout.notify import notify_agent
        from puser.models import site_admin_user
        notify_agent.send(site_admin_user, site_admin_user, 'circle/public_membership_approval', {
            'approval_link': link,
            'applicant': membership.member,
            'applicant_link': PUser.from_user(membership.member).get_absolute_url(),
            'circle': membership.circle,
            'membership': membership
        })
