from celery import shared_task


@shared_task
def dummy(x, y):
    return x + y


@shared_task
def activate_contract(contract):
    from contract.models import Contract
    if contract.status == Contract.Status.INITIATED.value:
        contract.activate()
        return True
    else:
        return False
