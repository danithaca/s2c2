from django.db.models.signals import post_save
from django.dispatch import receiver
from contract.models import Contract


# this automatically activates the contract.
# todo: add payment step.
@receiver(post_save, sender=Contract)
def auto_activate(sender, instance, created):
    if created and instance.status == Contract.Status.INITIATED.value:
        instance.activate()