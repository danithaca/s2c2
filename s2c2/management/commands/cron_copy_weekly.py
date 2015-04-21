import logging
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from location.models import Classroom
from slot.models import DayToken, OfferSlot
from user.models import GroupRole, UserProfile


class Command(BaseCommand):
    help = 's2c2 cron to copy staff/classroom schedule one week ahead based on the template base date.'

    def handle(self, *args, **options):
        # get today:
        today = DayToken.today()
        # logger = logging.getLogger('s2c2.management')

        # get all verified center staff
        staff_list = User.objects.filter(profile__isnull=False, profile__verified=True, profile__centers__isnull=False, groups__role__machine_name__in=GroupRole.center_staff_roles, profile__template_base_date__isnull=False).exclude(profile__template_copy_ahead='none').distinct()
        # logger.info('To process users: %d', len(staff_list))
        self.stdout.write('To process users: %d' % len(staff_list))
        for u in staff_list:
            staff = UserProfile(u)
            # only do it if the template base date is set.
            assert staff.has_profile() and staff.profile.template_base_date
            # logger.info('Processing %s' % staff.username)
            self.stdout.write('Processing %s' % staff.username)

            if staff.template_copy_ahead in ('1week', '2week', '3week', '4week'):
                week_num = int(staff.template_copy_ahead[0])
            else:
                week_num = 0

            source_day = DayToken(staff.template_base_date)
            target_day = today

            for w in range(week_num):
                target_week = target_day.expand_week()
                if OfferSlot.objects.filter(user=u, day__in=target_week).exists():
                    # will not copy due to existence of schedule (in any week).
                    # logger.warning('Target week is non empty: %s ~ %s' % (target_week[0].get_token(), target_week[-1].get_token()))
                    self.stdout.write('Target week is non empty: %s ~ %s' % (target_week[0].get_token(), target_week[-1].get_token()))
                else:
                    failed = OfferSlot.safe_copy_by_week(u, source_day, target_day)
                    if failed:
                        # logger.warning('Copy failed on date: %s', ','.join([d.get_token() for d in failed]))
                        self.stdout.write('Copy failed on date: %s', ','.join([d.get_token() for d in failed]))
                target_day = target_day.next_week()

        # get all valid classroom.
        classroom_list = Classroom.objects.filter(template_base_date__isnull=False, status=True).exclude(template_copy_ahead='none')
        self.stdout.write('To process classrooms: %d' % (classroom_list.count(),))
        for classroom in classroom_list:
            self.stdout.write('Processing %s' % classroom.name)
            assert classroom.template_base_date and classroom.template_copy_ahead != 'none'
            if classroom.template_copy_ahead in ('1week', '2week', '3week', '4week'):
                week_num = int(classroom.template_copy_ahead[0])
            else:
                week_num = 0

            source_day = DayToken(classroom.template_base_date)
            target_day = today
            for w in range(week_num):
                if source_day.is_same_week(target_day):
                    self.stderr.write('Same week. Do not copy')
                else:
                    classroom.copy_week_schedule(source_day, target_day)
                target_day = target_day.next_week()