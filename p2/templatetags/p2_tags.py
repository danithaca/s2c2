from django import template
from contract.models import Contract, Match


register = template.Library()


@register.simple_tag(name='contract-status')
def p2_tag_contract_status(status_code):
    status = Contract.Status(status_code)
    return status.name.capitalize()


@register.simple_tag(name='match-status')
def p2_tag_match_status(status_code):
    status = Match.Status(status_code)
    return status.name.capitalize()
