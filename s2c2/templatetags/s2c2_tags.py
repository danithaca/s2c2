import warnings

from django import template
from django.contrib.auth.models import User
from django.utils.dateformat import format

from log.models import Notification, Log
from slot.models import DayToken
from user.models import UserProfile
from location.models import Classroom, Center, Location


register = template.Library()


@register.filter
def bootstrap_alert(message):
    try:
        sub = message.tags if message.tags != 'error' else 'danger'
        return 'alert-%s' % sub
    except Exception:
        return ''


# @register.filter
# def display_name(user):
#     user_profile = UserProfile(user)
#     return user_profile.get_display_name()


@register.filter(name='name')
def s2c2_name(obj):
    """ This is the magic "filter" function that display things nicely in Template """
    #options = set(option_token.split(','))
    if isinstance(obj, User) or isinstance(obj, UserProfile):
        return obj.get_full_name() or obj.username
    elif isinstance(obj, Location):
        return obj.name


@register.simple_tag(name='icon')
def s2c2_icon(obj):
    if obj == 'unverified':
        # return '<i class="fa fa-ban"></i>'
        return '<span class="label label-danger" title="Please wait for your account to be verified."><i class="fa fa-ban"></i> unverified</span>'
    if isinstance(obj, User) or isinstance(obj, UserProfile) or obj == 'user':
        return '<i class="fa fa-user"></i>'
    elif isinstance(obj, Classroom) or obj == 'classroom':
        return '<i class="fa fa-paw"></i>'
    elif isinstance(obj, Center) or obj == 'center':
        return '<i class="fa fa-university"></i>'
    else:
        return ''


@register.simple_tag(name='classroom-icon')
def s2c2_classroom_icon():
    warnings.warn('Deprecated in favor or s2c2_icon', DeprecationWarning)
    return '<i class="fa fa-paw"></i>'


@register.filter
def nice_name(user):
    warnings.warn('Deprecated in favor or s2c2_name', DeprecationWarning)
    return user.get_full_name() or user.username


@register.simple_tag(name='link-a')
def link_a(a):
    # someday: not properly encoded. require caller to make sure things are encoded before pass in.
    assert isinstance(a, dict)
    legal_attr = ('href', 'class', 'title')
    if 'href' not in a:
        a['href'] = '#'
    tag_a_attr = ' '.join(['%s="%s"' % (attr, a[attr]) for attr in a if attr in legal_attr])
    if 'text' not in a:
        a['text'] = a['href']
    return '<a %s>%s</a>' % (tag_a_attr, a['text'])


@register.simple_tag(name='list-ul')
def list_ul(ul_class, items, none_label='-Empty-', empty_label='-None-'):
    if len(items) > 0:
        processed = []
        for i in items:
            if i is not None:
                s = '<li>%s</li>' % i
            else:
                s = '<li class="text-muted">%s</li>' % none_label
            processed.append(s)
        l = ''.join(processed)
    else:
        l = '<li class="text-muted">%s</li>' % empty_label

    return '<ul class="%s">%s</ul>' % (ul_class, l)


@register.simple_tag(name='day-regular-pager')
def slot_day_regular_pager(day, url):
    assert isinstance(day, DayToken)
    list_a = [(dt, link_a({
        'href': url + '?day=' + dt.get_token(),
        'text': '<i class="fa fa-calendar-o"></i> %s' % dt.display_weekday()
    })) for dt in (DayToken(d) for d in DayToken.weekday_tuple)]
    list_li = ['<li>%s</li>' % a if dt != day else '<li class="active">%s</li>' % a for dt, a in list_a]
    return '<ul class="pagination">%s</ul>' % ''.join(list_li)


@register.simple_tag(name='day-date-pager')
def slot_day_token_date_pager(day, url):
    assert isinstance(day, DayToken)
    list_data = []
    # list_data = [(day.prev_week(), '<i class="fa fa-fast-backward"></i>'), (day.prev_day(), '<i class="fa fa-step-backward"></i>')]
    list_data += [(dt, format(dt.value, 'M j, D')) for dt in day.expand_week()]
    # list_data += [(day.next_day(), '<i class="fa fa-step-forward"></i>'), (day.next_week(), '<i class="fa fa-fast-forward"></i>')]

    list_a = [(dt, link_a({
        'href': url + '?day=' + dt.get_token(),
        'text': '<i class="fa fa-calendar-o"></i> %s' % text
    })) for dt, text in list_data]

    list_li = ['<li>%s</li>' % a if dt != day else '<li class="active">%s</li>' % a for dt, a in list_a]
    return '<ul class="pagination">%s</ul>' % ''.join(list_li)


@register.filter
def show_notification_message(notification):
    assert isinstance(notification, Notification)
    # todo: add nicer display
    if notification.log.type == Log.OFFER_UPDATE:
        return 'Offer updated.'