from django import template
from django.contrib.auth.models import User
from django.templatetags.static import static
from image_cropping.templatetags.cropping import cropped_thumbnail
from contract.models import Contract, Match
from puser.models import PUser

register = template.Library()


@register.simple_tag(name='contract-status')
def p2_tag_contract_status(status_code):
    status = Contract.Status(status_code)
    return status.name.capitalize()


@register.simple_tag(name='match-status')
def p2_tag_match_status(status_code):
    status = Match.Status(status_code)
    return status.name.capitalize()


@register.simple_tag(takes_context=True)
def user_picture_url(context, puser, **kwargs):
    if isinstance(puser, User):
        puser = PUser.from_user(puser)

    assert isinstance(puser, PUser)
    if puser.has_picture():
        try:
            return cropped_thumbnail(context, puser.info, 'picture_cropping',upscale=True, **kwargs)
        except:
            # todo: add logging info.
            pass
    return static('user_200x200.png')