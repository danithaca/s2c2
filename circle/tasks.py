from celery import shared_task


@shared_task
def dummy(x, y):
    return x + y


# from puser.models import PUser
#
#
# @shared_task
# def handle_public_membership_approval(membership):
#     assert membership.circle.is_type_public() and membership.active
#     if not membership.approved:
#         # todo: do the real work with voucher
#         # right now, send to site admin.
#         link = '/admin/circle/membership/%d/' % membership.id
#         from shout.notify import notify_agent
#         notify_agent.send(None, None, 'circle/messages/public_membership_approval', {
#             'approval_link': link,
#             'applicant': membership.member,
#             'applicant_link': PUser.from_user(membership.member).get_absolute_url(),
#             'circle': membership.circle,
#             'membership': membership
#         })


# todo: if we use circle.apps.AppConfig in settings.py to register the circle app, then these tasks are not discovered.
# need to figure out what went wrong ...
@shared_task
def circle_invite(circle, member, initiate_user):
    """
    This is the hub that sends out invitation to the "member" user (new or existing) when s/he is added to the "circle" by "initiate_user".
    """
    member = member.to_puser()
    membership = circle.get_membership(member)

    from shout.notify import notify_agent
    #link = reverse('circle:parent')

    context = {
        # 'review_link': link,
        'circle': circle,
        'member': member
    }
    if not member.is_registered():
        context['signup_warning'] = True

    if initiate_user is None:
        initiate_user = circle.owner

    # todo: fix this
    if membership.is_valid_parent_relation():
        notify_agent.send(initiate_user, member, 'circle/messages/invited_parent', context)
    elif membership.is_valid_sitter_relation():
        notify_agent.send(initiate_user, member, 'circle/messages/invited_sitter', context)
    elif membership.is_valid_group_membership():
        notify_agent.send(initiate_user, member, 'circle/messages/invited_group', context)
