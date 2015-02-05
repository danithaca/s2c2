from django.contrib.auth.models import User
from django.core.management import BaseCommand
from user.models import GroupRole


class Command(BaseCommand):
    help = 's2c2 cron to copy regular schedule 3 days ahead.'

    def handle(self, *args, **options):
        # get all verified center staff
        staff_list = User.objects.filter(profile__isnull=False, profile__verified=True, centers__isnull=False, groups__role__machine_name__in=GroupRole.center_staff_roles)
        for u in staff_list:
            pass

        # get all classrooms
