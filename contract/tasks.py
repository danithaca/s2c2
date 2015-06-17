from celery import shared_task


@shared_task
def dummy(x, y):
    return x + y


@shared_task
def activate_contract(contract):
    contract.activate()
