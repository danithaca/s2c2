import logging
from celery import shared_task
from django.contrib.auth.models import User
from django.contrib.sites.models import Site, get_current_site
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from p2 import settings
from enum import Enum
from puser.models import PUser


class Notify(object):
    """
    This is the "facade" for all notifications purposes. Potentially allow SMS.
    This class is blocking. Use non-block methods in business logic.
    """

    class Method(Enum):
        EMAIL = 1
        SMS = 2
        EMAIL_SMS = 3

    def default_context(self):
        current_site = get_current_site()
        return {
            'site_name': current_site.name,
            'site_domain': current_site.domain,
            'site_url': 'http://%s' % current_site.domain,
            'current_site': current_site,
        }

    def send(self, from_user, to_user, tpl_prefix, ctx=None, anonymous=False):
        """
        Send notification regardless of the approach.
        """
        assert isinstance(from_user, User) and (isinstance(to_user, User) or all([isinstance(u, User) for u in to_user]))

        subject_tpl = tpl_prefix + '_subject.txt'
        body_tpl = tpl_prefix + '_body.txt'

        context = self.default_context()
        context.update(ctx)

        subject = render_to_string(subject_tpl, context)
        subject = ''.join(subject.splitlines())
        body = render_to_string(body_tpl, context)

        if isinstance(to_user, User):
            to_user_list = [to_user]
        else:
            to_user_list = to_user

        messages_list = []
        for u in to_user_list:
            if anonymous:
                # if using bcc, then send message to 'from_user', put message in bcc.
                msg = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=[from_user.email], reply_to=[from_user.email], bcc=[u.email])
            else:
                msg = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=[u.email], reply_to=[from_user.email])
            messages_list.append(msg)

        connection = get_connection(fail_silently=True)       # use the default email settings
        return connection.send_messages(messages_list)

    # def send_single_email(self, email_reply, email_to, subject_tpl, body_tpl, ctx, bcc=False):
    #     """
    #     Send email either using TO or BCC
    #     :param email_reply: the 'reply-to' field. The "From" field is always settings.DEFAULT_EMAIL_FROM
    #     :param email_to: either a single email address or a list of addresses.
    #     :param subject_tpl: template for subject
    #     :param body_tpl: template for body
    #     :param ctx: ctx to render the template
    #     :param bcc: False will put all "email_to" in "TO", which is visible to everyone; True put into BCC and use 'reply-to' in 'TO'.
    #     :return: # of emails sent
    #     """
    #     logging.debug('send_single_email executed: %s - %s' % (email_reply, email_to))
    #
    #     # python3, string type is 'str', python2 is 'basestring'
    #     if isinstance(email_to, str):
    #         email_to_list = [email_to, ]
    #     else:
    #         email_to_list = email_to
    #
    #     assert isinstance(email_reply, str)
    #
    #     subject = render_to_string(subject_tpl, ctx)
    #     subject = ''.join(subject.splitlines())
    #     body = render_to_string(body_tpl, ctx)
    #     # connection = get_connection(fail_silently=True)       # use the default email settings
    #
    #     if bcc:
    #         msg = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=[email_reply], reply_to=[email_reply], bcc=email_to_list)
    #     else:
    #         msg = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=email_to_list, reply_to=[email_reply])
    #
    #     return msg.send()

    #def send_multiple_email(self, email_reply, email_to_list, ):


notify_agent = Notify()
site_admin_user = PUser.get_or_create(settings.DEFAULT_FROM_EMAIL)
