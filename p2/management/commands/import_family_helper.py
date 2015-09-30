import logging
import json
import os
import html
import re

from django.core.management import BaseCommand
from django.conf import settings

from circle.models import Circle
from puser.models import PUser, Area


class Command(BaseCommand):
    help = 'Import UM family helper into database'

    def handle(self, *args, **options):
        with open(os.path.join(settings.DATA_DIR, 'family_helper_crawl.json'), 'r') as f:
            data = json.load(f)
            logging.info("Total records: %d" % len(data))
            emails = []

            helper_circle = Circle.objects.get(type=Circle.Type.AGENCY.value, name__icontains='family helper', area=Area.default())

            for record in data:
                # if record['services'].lower().find('child care') != -1:
                name_tuple = html.unescape(record['name']).split()
                first_name, last_name = name_tuple[0], name_tuple[-1]
                email = record['email']
                emails.append(email)
                m = re.match(r'\((\d{3})\) (\d{3})-(\d{4})', record['phone'])
                assert m is not None
                phone = "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
                note = html.unescape(record['note'])

                # create user account
                if not PUser.objects.filter(email=email).exists():
                    created_user = PUser.create(email, area=Area.default())
                    created_user.first_name = first_name
                    created_user.last_name = last_name
                    created_user.save()
                    created_user.info.phone = phone
                    created_user.info.note = note
                    created_user.info.save()

                    # assign user to family helper circle
                    helper_circle.add_member(created_user, approved=True)

            # print list of emails for notification.
            print(','.join(emails))