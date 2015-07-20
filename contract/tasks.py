from celery import shared_task


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