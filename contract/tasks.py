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
    from puser.models import site_admin_user
    notify_agent.send(site_admin_user, contract.initiate_user, 'contract/messages/contract_activated', {'contract': contract})


@shared_task
def after_match_accepted(match):
    from shout.notify import notify_agent
    notify_agent.send(match.target_user, match.contract.initiate_user, 'contract/messages/match_accepted', {'match': match, 'contract': match.contract})