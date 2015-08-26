from account.models import SignupCode
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
        notify_agent.send(None, None, 'circle/public_membership_approval', {
            'approval_link': link,
            'applicant': membership.member,
            'applicant_link': PUser.from_user(membership.member).get_absolute_url(),
            'circle': membership.circle,
            'membership': membership
        })


@shared_task
def personal_circle_send_invitation(circle, target_user):
    target_user = PUser.from_user(target_user)
    if target_user.is_registered():
        link = reverse('circle:manage_loop')
        from shout.notify import notify_agent
        notify_agent.send(circle.owner, target_user, 'circle/personal_membership_notice', {
            'review_link': link,
            'circle_owner': circle.owner,
        })
    else:
        # user is not active. send invitation code
        expiry = 24 * 365   # a year to expire. in hours.
        try:
            signup_code = SignupCode.create(email=target_user.email, expiry=expiry, inviter=circle.owner)
            signup_code.send(extra_ctx={
                'inviter': circle.owner.get_name()
            })
        except SignupCode.AlreadyExists:
            # todo: figure out what to do when invitation code is alreay sent.
            # current we do nothing, assuming the target user already received a invitation email
            pass
