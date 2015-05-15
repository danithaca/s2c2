from abc import ABCMeta
from datetime import timedelta
import warnings
from django.core.urlresolvers import reverse

from django.db import models
from django.contrib.auth.models import User


# specifies when to create a new log entry or when to update instead.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import capfirst
from location.models import Location, Classroom, Center
from user.models import UserProfile
from django.utils import timezone


NO_UPDATE_INTERVAL = timedelta(hours=2)


class Log(models.Model):
    # OFFER_REGULAR_UPDATE = 1   # obsolete
    # OFFER_DATE_UPDATE = 2      # obsolete
    # NEED_REGULAR_UPDATE = 3    # obsolete
    # NEED_DATE_UPDATE = 4       # obsolete

    OFFER_UPDATE = 5
    NEED_UPDATE = 6

    MEET_UPDATE = 7
    # MEET_ADD = 8
    # MEET_DELETE = 9
    MEET_CASCADE_DELETE_OFFER = 16
    MEET_CASCADE_DELETE_NEED = 17
    MEET_SPECIAL_UPDATE = 18

    # this implies it's "offer" update
    TEMPLATE_OP_STAFF = 11
    # this implies it's "need/meet" update
    TEMPLATE_OP_CLASSROOM = 12

    SIGNUP = 13
    COMMENT_BY_LOCATION = 14
    VERIFY = 15

    LOG_TYPE = (
        # (TYPE_OFFER_REGULAR_UPDATE, 'Update: offer regular'),
        # (TYPE_OFFER_DATE_UPDATE, 'Update: offer date'),
        # (TYPE_NEED_REGULAR_UPDATE, 'Update: need regular'),
        # (TYPE_NEED_DATE_UPDATE, 'Update: need date'),
        (OFFER_UPDATE, 'staff availability update'),
        (NEED_UPDATE, 'classroom need update'),
        (MEET_UPDATE, 'assignment update'),
        (MEET_CASCADE_DELETE_OFFER, 'assignment canceled due to staff availability change'),
        (MEET_CASCADE_DELETE_NEED, 'assignment canceled due to classroom need change'),
        (TEMPLATE_OP_STAFF, 'staff template operation'),
        (TEMPLATE_OP_STAFF, 'classroom template operation'),
        (SIGNUP, 'user signup'),
        (COMMENT_BY_LOCATION, 'comment'),
        (VERIFY, 'user verification'),
        (MEET_SPECIAL_UPDATE, 'staff availability update')
    )

    creator = models.ForeignKey(User)
    type = models.PositiveSmallIntegerField(choices=LOG_TYPE, help_text='The type of the log entry.')
    ref = models.CommaSeparatedIntegerField(help_text='ID of the entity in question. Handled by the particular type.', max_length=100)
    message = models.TextField(blank=True, help_text='Addition human-readable message.')
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s: %s (%s)' % (self.creator.username, self.ref, self.get_type_display())

    # someday: might want to migrate to LogObject.
    def display(self):
        from slot.models import DayToken, TimeToken
        message = self.message
        # if self.type == Log.OFFER_UPDATE:
        #     return 'updated availability (%s)' % self.message
        # elif self.type == Log.NEED_UPDATE:
        #     return 'updated needs: %s' % self.message
        try:
            if self.type in (Log.TEMPLATE_OP_STAFF, Log.TEMPLATE_OP_CLASSROOM):
                # day = DayToken.from_token(self.ref.split(',')[1])
                message = 'copied from template'
            elif self.type == Log.MEET_UPDATE:
                staff_id, classroom_id, d, t = self.ref.split(',')
                t = TimeToken.from_token(t)
                # message = 'assignment updated (%s): %s' % (t.display(), message)
                message = '%s' % (t.display(),)
            elif self.type == Log.MEET_CASCADE_DELETE_OFFER:
                staff_id, classroom_id, d, t = self.ref.split(',')
                staff = UserProfile.get_by_id(staff_id)
                t = TimeToken.from_token(t)
                message = '%s on %s' % (staff.get_display_name(), t.display())
            elif self.type == Log.MEET_CASCADE_DELETE_NEED:
                staff_id, classroom_id, d, t = self.ref.split(',')
                classroom = Classroom.get_by_id(classroom_id)
                t = TimeToken.from_token(t)
                message = '%s on %s' % (classroom.name, t.display())
            elif self.type == Log.SIGNUP:
                staff = UserProfile.get_by_id(self.ref)
                if not message:
                    message = '"%s" signed up' % staff.get_display_name()
                else:
                    message = '"%s" %s' % (staff.get_display_name(), message)
            elif self.type == Log.VERIFY:
                staff = UserProfile.get_by_id(self.ref)
                message = '"%s" verified' % staff.get_display_name()
        except (User.DoesNotExist, Location.DoesNotExist):
            message = '%s (entity invalid)' % message

        return message

    @staticmethod
    def create(t, creator, data, message='', force=False):
        from slot.models import DayToken, TimeToken
        ref = None
        if t in (Log.OFFER_UPDATE, Log.NEED_UPDATE):
            target, day = data
            assert isinstance(target, User) or isinstance(target, UserProfile) or isinstance(target, Location)
            assert isinstance(day, DayToken)
            ref = '%d,%s' % (target.pk, day.get_token())
        elif t in (Log.MEET_UPDATE, Log.MEET_CASCADE_DELETE_OFFER, Log.MEET_CASCADE_DELETE_NEED):
            staff, classroom, day, start_time = data
            assert isinstance(staff, User) and isinstance(classroom, Location) and isinstance(day, DayToken) and isinstance(start_time, TimeToken)
            ref = '%d,%d,%s,%s' % (staff.pk, classroom.pk, day.get_token(), start_time.get_token())
        elif t in (Log.MEET_SPECIAL_UPDATE,):
            staff, location, day, start_time = data
            assert isinstance(staff, User) and isinstance(location, Location) and isinstance(day, DayToken) and isinstance(start_time, TimeToken)
            ref = '%d,%d,%s,%s' % (staff.pk, location.pk, day.get_token(), start_time.get_token())
        elif t in (Log.TEMPLATE_OP_STAFF, Log.TEMPLATE_OP_CLASSROOM):
            target, day = data
            assert isinstance(target, User) or isinstance(target, Location)
            assert isinstance(day, DayToken) and not day.is_regular()
            ref = '%d,%s' % (target.pk, day.get_token())
        elif t in (Log.SIGNUP, Log.VERIFY):
            u = data[0]
            assert len(data) == 1 and isinstance(u, User)
            ref = str(u.pk)

        # todo: create or update based on time elapse.
        entry = Log(creator=creator, type=t, ref=ref, message=message)
        entry.save()

    @staticmethod
    def create_comment_by_location(creator, location, day, comment):
        entry = Log(creator=creator, type=Log.COMMENT_BY_LOCATION, ref='%d,%s' % (location.id, day.get_token()), message=comment)
        entry.save()

    def is_today(self):
        return timezone.now().date() == self.updated.date()

    def get_links(self):
        """
        :return: list of link data to be imported to link_a
        """
        ref_list = self.ref.split(',')
        links = []
        try:
            if self.type in (Log.OFFER_UPDATE, Log.TEMPLATE_OP_STAFF):
                u = User.objects.get(pk=ref_list[0])
                links.append({'text': 'view availability', 'href': '%s?day=%s' % (reverse('cal:staff', kwargs={'uid': u.pk}), ref_list[1])})

            elif self.type in (Log.NEED_UPDATE, Log.TEMPLATE_OP_CLASSROOM):
                classroom = Classroom.objects.get(pk=ref_list[0])
                links.append({'text': 'view availability', 'href': '%s?day=%s' % (reverse('cal:classroom', kwargs={'cid': classroom.pk}), ref_list[1])})

            elif self.type in (Log.MEET_UPDATE, Log.MEET_CASCADE_DELETE_OFFER, Log.MEET_CASCADE_DELETE_NEED):
                staff_id, classroom_id, d, t = self.ref.split(',')
                u = User.objects.get(pk=ref_list[0])
                links.append({'text': 'view availability', 'href': '%s?day=%s' % (reverse('cal:staff', kwargs={'uid': u.id}), d)})
                classroom = Classroom.objects.get(pk=ref_list[0])
                links.append({'text': 'view availability', 'href': '%s?day=%s' % (reverse('cal:classroom', kwargs={'cid': classroom.id}), d)})

            elif self.type in (Log.SIGNUP, Log.VERIFY):
                staff = User.objects.get(pk=self.ref)
                links.append({'text': 'view availability', 'href': '%s' % (reverse('cal:staff', kwargs={'uid': staff.pk}))})

            elif self.type == Log.COMMENT_BY_LOCATION:
                location_id, day = self.ref.split(',')
                links.append({'text': 'view wall', 'href': '%s?day=%s&view=agendaDay' % (reverse('cal:center', kwargs={'cid': location_id}), day)})

        except (User.DoesNotExist, Location.DoesNotExist):
            pass

        return links

    # def get_creator_name(self):
    #     return self.creator.get_full_name() or self.creator.username


# this is the proxy class to Log. for different not implemented yet.
class LogObject(metaclass=ABCMeta):
    def __init__(self, log):
        self.log = log

    def to_notification(self):
        pass


class Notification(models.Model):
    sender = models.ForeignKey(User, null=True, blank=True, related_name='notification_sender')
    receiver = models.ForeignKey(User, related_name='notification_receiver')

    # this is required, which means every notification would have a log, not vice versa.
    log = models.ForeignKey(Log)

    # mark whether the receiver has viewed it or not.
    done = models.BooleanField(default=False)

    LEVEL_HIGH = 10         # any thing that requires special attention should be 'high'.
    LEVEL_NORMAL = 20       # usually notification should be on normal level
    LEVEL_LOW = 30
    LEVELS = (
        (LEVEL_HIGH, 'high'),
        (LEVEL_NORMAL, 'normal'),
        (LEVEL_LOW, 'low'),
    )
    level = models.SmallIntegerField(choices=LEVELS, help_text='priority level of the notification.')

    # this could be different from Log.updated.
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def create(log, sender, receiver, level):
        assert isinstance(sender, User) and isinstance(receiver, User)
        notification = Notification(sender=sender, receiver=receiver, log=log, level=level, done=False)
        notification.save()

    @staticmethod
    def my_unread_count(receiver):
        return Notification.objects.filter(receiver=receiver, done=False).count()

    def is_today(self):
        return timezone.now().date() == self.created.date()

    def display(self):
        if self.log.type == Log.COMMENT_BY_LOCATION:
            prefix = 'Wall post'
        else:
            prefix = capfirst(self.log.get_type_display())

        message = self.log.display()
        return '%s - %s' % (prefix, message)


@receiver(post_save, sender=Log)
def log_to_notification(sender, **kwargs):
    log = kwargs['instance']

    try:
        # create notification if "offer" is not updated by me.
        if log.type in (Log.OFFER_UPDATE, Log.TEMPLATE_OP_STAFF):
            target_id = int(log.ref.split(',')[0])
            if log.creator is not None and log.creator.pk != target_id:
                u = User.objects.get(pk=target_id)
                Notification.create(log, log.creator, u, Notification.LEVEL_NORMAL)

        # notify staff who are affected due to assignment change from the classrooms.
        elif log.type in (Log.MEET_UPDATE, Log.MEET_CASCADE_DELETE_NEED):
            target_id = int(log.ref.split(',')[0])
            u = User.objects.get(pk=target_id)
            Notification.create(log, log.creator, u, Notification.LEVEL_NORMAL)

        # notify all center managers if assignment change due to staff availability problems.
        elif log.type == Log.MEET_CASCADE_DELETE_OFFER:
            # someday: might want to check if it is the center managers who changed the offer. if so, no need to send notifications.
            target_id, location_id, day_token, time_token = log.ref.split(',')
            target_user = User.objects.get(pk=target_id)
            classroom = Classroom.objects.get(pk=location_id)
            center = classroom.center
            for manager in center.get_managers():
                Notification.create(log, log.creator, manager, Notification.LEVEL_HIGH)

        elif log.type == Log.SIGNUP:
            target_user = UserProfile.get_by_id(log.ref)
            if target_user.has_profile() and target_user.profile.centers.exists():
                for center in target_user.profile.centers.all():
                    for manager in center.get_managers():
                        # usually target_user.user == log.creator, but not necessarily
                        Notification.create(log, target_user.user, manager, Notification.LEVEL_NORMAL)

        elif log.type == Log.VERIFY:
            target_user = UserProfile.get_by_id(log.ref)
            Notification.create(log, log.creator, target_user.user, Notification.LEVEL_HIGH)

        elif log.type == Log.COMMENT_BY_LOCATION:
            creator = UserProfile(log.creator)
            location_id, day = log.ref.split(',')
            center = Center.objects.get(pk=location_id)
            if creator.is_center_staff():
                # notify all center mangers.
                for manager in center.get_managers():
                    Notification.create(log, creator.user, manager, Notification.LEVEL_NORMAL)
            elif creator.is_center_manager():
                # notify all related people, except for the manager herself.
                target_list = Log.objects.filter(type=Log.COMMENT_BY_LOCATION, ref=log.ref).exclude(creator=creator.user).values_list('creator', flat=True)
                for target_id in target_list:
                    target_user = User.objects.get(pk=target_id)
                    Notification.create(log, creator.user, target_user, Notification.LEVEL_NORMAL)

    except (User.DoesNotExist, Location.DoesNotExist, Classroom.DoesNotExist, Center.DoesNotExist):
        pass