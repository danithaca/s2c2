import logging
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from slot.models import DayToken, OfferSlot
from user.models import GroupRole, UserProfile


class Command(BaseCommand):
    help = 's2c2 cron to copy staff schedule one week ahead based on the template base date.'

    def handle(self, *args, **options):
        # get today:
        today = DayToken.today()
        # logger = logging.getLogger('s2c2.management')

        # get all verified center staff
        staff_list = User.objects.filter(profile__isnull=False, profile__verified=True, profile__centers__isnull=False, groups__role__machine_name__in=GroupRole.center_staff_roles).distinct()
        # logger.info('To process users: %d', len(staff_list))
        self.stdout.write('To process users: %d' % len(staff_list))
        for u in staff_list:
            staff = UserProfile(u)
            # only do it if the template base date is set.
            if staff.has_profile() and staff.profile.template_base_date:
                # logger.info('Processing %s' % staff.username)
                self.stdout.write('Processing %s' % staff.username)
                next_week = today.next_week()
                next_next_week = next_week.next_week()
                for target_day in (next_week, next_next_week):
                    target_week = target_day.expand_week()
                    if OfferSlot.objects.filter(user=u, day__in=target_week).exists():
                        # will not copy due to existence of schedule (in any week).
                        # logger.warning('Target week is non empty: %s ~ %s' % (target_week[0].get_token(), target_week[-1].get_token()))
                        self.stdout.write('Target week is non empty: %s ~ %s' % (target_week[0].get_token(), target_week[-1].get_token()))
                        continue
                    else:
                        from_day = DayToken(staff.profile.template_base_date)
                        failed = OfferSlot.safe_copy_by_week(u, from_day, target_day)
                        if failed:
                            # logger.warning('Copy failed on date: %s', ','.join([d.get_token() for d in failed]))
                            self.stdout.write('Copy failed on date: %s', ','.join([d.get_token() for d in failed]))
            else:
                # logger.info('No copy schedule for %s' % staff.username)
                self.stdout.write('No copy schedule for %s' % staff.username)