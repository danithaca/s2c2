from celery import shared_task
from datetime import datetime, timedelta
from django.utils.timezone import localtime, now


@shared_task
def dummy(x, y):
    return x + y


@shared_task
def after_contract_activated(contract):
    # compute matches
    from contract.algorithms import L1Recommender
    recommender = L1Recommender()
    recommender.recommend(contract)

    from shout.notify import notify_agent
    notify_agent.send(None, contract.initiate_user, 'contract/messages/contract_activated', {'contract': contract})


@shared_task
def after_contract_confirmed(contract):
    from shout.notify import notify_agent
    confirmed_match = contract.confirmed_match
    # first, shout to the target user
    notify_agent.send(contract.initiate_user, confirmed_match.target_user, 'contract/messages/contract_confirmed_send',
                      {'match': confirmed_match, 'contract': contract, 'initiate_user': contract.initiate_user})
    # next, shout to the initiate user
    notify_agent.send(confirmed_match.target_user, contract.initiate_user, 'contract/messages/contract_confirmed_review',
                      {'match': confirmed_match, 'contract': contract, 'target_user': confirmed_match.target_user})
    # schedule reminder tasks
    # fixme: if contract is confirmed and then undo and then confirmed again. we want to make sure it doesn't have problems
    before_contract_starts.apply_async((contract,), eta=contract.event_start - timedelta(hours=1))
    after_contract_ends.apply_async((contract,), eta=contract.event_end + timedelta(hours=6))
    handle_expired_contract.apply_async((contract,), eta=contract.event_end + timedelta(days=2))


@shared_task
def before_contract_starts(contract):
    from shout.notify import notify_agent
    from puser.models import PUser
    # make sure contract is not canceled at the moment and within 2 hours of time.
    if contract.is_confirmed() and contract.is_event_upcoming() and contract.event_start - timedelta(hours=2) < now():
        client = contract.initiate_user
        server = contract.confirmed_match.target_user
        ctx = {
            'client': PUser.from_user(client),
            'server': PUser.from_user(server),
            # todo: make sure timezone is correct.
            'event_start': localtime(contract.event_start),
            'contract': contract,
            'match': contract.confirmed_match,
        }
        notify_agent(client, server, 'contract/messages/start_reminder_server', ctx)
        notify_agent(server, client, 'contract/messages/start_reminder_client', ctx)


@shared_task
def after_contract_ends(contract):
    from shout.notify import notify_agent
    from puser.models import PUser
    # make sure contract is not canceled at the moment and contract is expired.
    if contract.is_confirmed() and contract.is_event_expired():
        client = contract.initiate_user
        server = contract.confirmed_match.target_user
        ctx = {
            'client': PUser.from_user(client),
            'server': PUser.from_user(server),
            # todo: make sure timezone is correct.
            'event_start': localtime(contract.event_start),
            'contract': contract,
        }
        notify_agent(None, client, 'contract/messages/end_reminder_client', ctx)


@shared_task
def handle_expired_contract(contract):
    # make sure it's at least 1 day after it expired.
    if contract.is_confirmed() and contract.is_event_expired() and now() > contract.event_end + timedelta(days=1):
        contract.succeed()


@shared_task
def after_match_accepted(match):
    from shout.notify import notify_agent
    notify_agent.send(match.target_user, match.contract.initiate_user, 'contract/messages/match_accepted', {'match': match, 'contract': match.contract})


@shared_task
def after_match_engaged(match):
    from shout.notify import notify_agent
    notify_agent.send(match.contract.initiate_user, match.target_user, 'contract/messages/match_engaged', {'match': match, 'contract': match.contract})


@shared_task
def after_contract_reverted(contract, match):
    from shout.notify import notify_agent

    # shout to the affected target user
    notify_agent.send(contract.initiate_user, match.target_user, 'contract/messages/contract_reverted',
                      {'match': match, 'contract': contract, 'initiate_user': contract.initiate_user})
    # next, shout to the initiate user
    # notify_agent.send(site_admin_user, contract.initiate_user, 'contract/messages/contract_reverted_review',
    #                   {'match': match, 'contract': contract, 'target_user': match.target_user})


@shared_task
def after_contract_failed(contract):
    from shout.notify import notify_agent
    notify_agent.send(None, None, 'contract/messages/contract_failed', {'contract': contract})


@shared_task
def after_contract_updated(contract):
    # send all "accepted" servers the updated info notes.
    from shout.notify import notify_agent
    from contract.models import Match
    for match in contract.match_set.filter(status=Match.Status.ACCEPTED.value):
        notify_agent.send(contract.initiate_user, match.target_user, 'contract/messages/contract_updated',
                          {'contract': contract, 'match': match})


@shared_task
def after_contract_canceled(contract):
    if not contract.is_event_expired():
        from shout.notify import notify_agent
        from contract.models import Match
        for match in contract.match_set.filter(status=Match.Status.ACCEPTED.value):
            notify_agent.send(contract.initiate_user, match.target_user, 'contract/messages/contract_canceled',
                              {'contract': contract, 'match': match})
