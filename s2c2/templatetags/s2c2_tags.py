from django import template
from django.utils.dateformat import format

from slot.models import DayToken
from user.models import UserProfile


register = template.Library()


@register.filter
def bootstrap_alert(message):
    try:
        sub = message.tags if message.tags != 'error' else 'danger'
        return 'alert-%s' % sub
    except Exception:
        return ''


@register.filter
def display_name(user):
    user_profile = UserProfile(user)
    return user_profile.get_display_name()


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
    list_data = [(day.prev_week(), '<i class="fa fa-fast-backward"></i>'), (day.prev_day(), '<i class="fa fa-step-backward"></i>')]
    list_data += [(dt, format(dt.value, 'M j (D)')) for dt in day.expand_week()]
    list_data += [(day.next_day(), '<i class="fa fa-step-forward"></i>'), (day.next_week(), '<i class="fa fa-fast-forward"></i>')]

    list_a = [(dt, link_a({
        'href': url + '?day=' + dt.get_token(),
        'text': text
    })) for dt, text in list_data]

    list_li = ['<li>%s</li>' % a if dt != day else '<li class="active">%s</li>' % a for dt, a in list_a]
    return '<ul class="pagination">%s</ul>' % ''.join(list_li)
