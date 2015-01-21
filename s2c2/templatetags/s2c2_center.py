from django import template
from django.core.urlresolvers import reverse
from s2c2.templatetags.s2c2_tags import link_a, s2c2_icon, s2c2_name, list_ul
from slot.models import TimeSlot


register = template.Library()


@register.simple_tag(name='classroom-day-staff')
def s2c2_classroom_day_staff(classroom, day):
    day_staff = classroom.get_staff(day)
    items = [link_a({
        'href': reverse('dashboard', kwargs={'uid': u.pk}),
        'text': s2c2_icon('user') + ' ' + s2c2_name(u)
    }) for u in day_staff]
    return list_ul('list-inline', items)


@register.simple_tag(name='classroom-day-unmet-need')
def s2c2_classroom_day_unmet_need(classroom, day):
    items = []
    list_timetoken = classroom.get_unmet_need_time(day)
    if len(list_timetoken) > 0:
        items = [t.display() for t in TimeSlot.combine(list_timetoken)]
    return list_ul('list-inline', items)