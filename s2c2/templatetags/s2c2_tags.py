from django import template
from django.core.urlresolvers import reverse
from slot.models import DayOfWeek

register = template.Library()


@register.filter
def bootstrap_alert(message):
    try:
        sub = message.tags if message.tags != 'error' else 'danger'
        return 'alert-%s' % sub
    except Exception:
        return ''


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


@register.simple_tag(name='dow-pager')
def slot_dow_pager(dow):
    assert isinstance(dow, DayOfWeek), type(dow)
    # generate list of <a>
    list_a = [(d, link_a({
        'href': reverse('slot:staff_regular') + '?dow=' + str(d),
        'text': '<i class="fa fa-calendar-o"></i> %s' % DayOfWeek.get_name(d)
    })) for d in DayOfWeek.get_tuple()]
    list_li = ['<li>%s</li>' % a if d != dow.dow else '<li class="active">%s</li>' % a for d, a in list_a]
    return '<ul class="pagination">%s</ul>' % ''.join(list_li)
