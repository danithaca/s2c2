# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
# from circle.models import Membership
# from circle.tasks import handle_public_membership_approval
#
#
# @receiver(post_save, sender=Membership)
# def public_membership_approval(sender, instance=None, created=None, **kwargs):
#     if instance.circle.is_type_public() and instance.active and not instance.approved:
#         # send out approval link.
#         # using "delay" seems to generate issues related to dictionary key changes in serialization
#         #handle_public_membership_approval.delay(instance)
#         handle_public_membership_approval(instance)
