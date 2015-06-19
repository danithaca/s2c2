import logging
from celery import shared_task
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from p2 import settings


def shout_single_email(email_reply, email_to, subject_tpl, body_tpl, context, bcc=False):
    """
    Send email either using TO or BCC
    :param email_reply: the 'reply-to' field. The "From" field is always settings.DEFAULT_EMAIL_FROM
    :param email_to: either a single email address or a list of addresses.
    :param subject_tpl: template for subject
    :param body_tpl: template for body
    :param context: context to render the template
    :param bcc: False will put all "email_to" in "TO", which is visible to everyone; True put into BCC and use 'reply-to' in 'TO'.
    :return: # of emails sent
    """
    logging.debug('shout_signle_email executed: %s - %s' % (email_reply, email_to))

    # python3, string type is 'str', python2 is 'basestring'
    if isinstance(email_to, str):
        email_to_list = [email_to, ]
    else:
        email_to_list = email_to

    assert isinstance(email_reply, str)

    subject = render_to_string(subject_tpl, context)
    subject = ''.join(subject.splitlines())
    body = render_to_string(body_tpl, context)
    # connection = get_connection(fail_silently=True)       # use the default email settings

    if bcc:
        msg = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=[email_reply], reply_to=[email_reply], bcc=email_to_list)
    else:
        msg = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=email_to_list, reply_to=[email_reply])

    return msg.send()


def get_default_context():
    # shout_default_site_name = Site.objects.get_current().name.lower()
    # shout_default_context = {
    #     'site_name': shout_default_site_name,
    #     'site_url': 'http://%s' % shout_default_site_name
    # }
    return {
        'site_name': 'Servuno',
        'site_domain': 'servuno.com',
        'site_url': 'http://servuno.com',
    }


@shared_task
def shout_match_accepted(match):
    from contract.models import Match
    assert isinstance(match, Match) and match.is_accepted()
    email_reply = match.target_user.email
    email_to = match.contract.initiate_user.email

    context = get_default_context()
    context.update({
        'target_user_name': settings.ACCOUNT_USER_DISPLAY(match.target_user),
        'contract_count_accepted': match.contract.count_accepted_match(),
        'contract_url': context['site_url'] + match.contract.get_absolute_url()
    })

    subject_tpl = 'contract/email/match_accepted_subject.txt'
    body_tpl = 'contract/email/match_accepted_body.txt'

    shout_single_email(email_reply, email_to, subject_tpl, body_tpl, context)