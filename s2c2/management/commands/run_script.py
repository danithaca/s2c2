from django.contrib.auth.models import User
from django.core.management import BaseCommand
import re
from location.models import Center
from user.models import Profile, GroupRole


def import_users():
    full_time = """
Elena Avedisova <lenaa@umich.edu>,
Michelle Freund <freundm@umich.edu>,
Sandra Brown <brownsan@umich.edu>,
Amy McCarley <cristamy@umich.edu>,
Kumiko Ito-Teitgen <kteitgen@umich.edu>,
Joseph Foster <jafoste@umich.edu>,
Abosede Adeyoju <wemimo@umich.edu>,
Nichole Williams <nmwilli@umich.edu>,
Stacia Hill <stacialh@umich.edu>,
Stacy Wright <wrightsw@umich.edu>,
Tiffany Lopez <tnlopez@umich.edu>,
Laura MacGregor <lgmacgr@umich.edu>,
Seth Brown <sabrown@umich.edu>,
Sabrina North <smenorth@umich.edu>,
Julia Koumbassa <juliako@umich.edu>,
Emily Fanelli <eblaw@umich.edu>,
Joan Rehak <jrehak@umich.edu>,
Mary Crison <crisonmc@umich.edu>,
Laney Hoatlin <lhoatlin@umich.edu>,
Tracy Winkelman <twink@umich.edu>,
Charlene Cone <cacone@umich.edu>,
Leslie Elliott <lwelliot@umich.edu>,
Catherine Wood <cpwo@umich.edu>,
Jordan Sabolish <jsabolish@gmail.com>,
Christine White <cuspard@umich.edu>,
Jillian Guenther <ljillian@umich.edu>,
Kathe Harrigan <katheh@umich.edu>,
Kc Carlson <kccarls@umich.edu>,
Yvonne Porter <yvporter@umich.edu>,
Mollie Bogan <molliebo@umich.edu>
"""
    part_time = """
Abigail Orrick <abbyo@umich.edu>,
Alyssa Henderson <alyssahe@umich.edu>,
Amber Cicalo <ambmarie@umich.edu>,
Asana Onishi <aonishi@umich.edu>,
Dani Vieni <dvieni@umich.edu>,
Duy Mo <duymo@umich.edu>,
Elizabeth Corace <eacor@umich.edu>,
Ellen Guerra <elguerra@umich.edu>,
Hyejin Lee <hyejinl@umich.edu>,
Ian Williams <imwill@umich.edu>,
Joshua Lee <joshsung@umich.edu>,
Kaitlyn Blackburn <kblackb@umich.edu>,
Katherine Weidmayer <kweidmay@umich.edu>,
Kathryn Sheldon <kdhancoc@umich.edu>,
Kayla Winer <kaywiner@umich.edu>,
Lisel Neumann <liseln@umich.edu>,
Marisa Diamond <marisad@umich.edu>,
Meagan Williams <meaganw@umich.edu>,
Sanjay Das <sanjaykd@umich.edu>,
Skyler Kragt <skylerk@umich.edu>,
Sophia Rex <sophiare@umich.edu>,
Stephanie Bostwick <bostwics@umich.edu>,
Tori Cushard <tcushard@umich.edu>,
Connor Pollock <cpnd@umich.edu>,
Johanna Fritts <jlfritts@umich.edu>,
Shakiera Ibrahim <ssibrahi@umich.edu>,
NCCC staff <nccc.staff@umich.edu>,
Jan Bower <jllbower@yahoo.com>,
Theresa Spinei <treespin@umich.edu>,
Theresa Spinei <treespinei@comcast.net>,
Carine Lutz <c.l.photo@earthlink.net>,
Lina Abdulhamid <linaabdulhamid@yahoo.com>,
Caitlin Concannon <cconc@umich.edu>,
Jordan Sabolish <jsabolish@gmail.com>,
Erin McKenna <mserinmckenna@gmail.com>,
Xiaoxin Li <xiaoxinl@umich.edu>
"""
    teacher_group = GroupRole.get_by_name('teacher').group
    sub_group = GroupRole.get_by_name('support').group
    north_campus = Center.objects.get(name='North Campus')
    for line in full_time.splitlines():
        m = re.match(r'''^([a-zA-Z- ]+) ([a-zA-Z- ]+) \<([a-zA-Z0-9.]+\@\w+\.\w+)\>.*$''', line)
        if m:
            first_name, last_name, email = m.group(1), m.group(2), m.group(3)
            #print(m.group(1), m.group(2), m.group(3))
            try:
                u = User.objects.get(email=email)
                if not u.first_name or not u.last_name :
                    u.first_name = first_name
                    u.last_name = last_name
                    u.save()

                try:
                    p = u.profile
                    if not p.verified:
                        p.verified = True
                        p.save()
                except Profile.DoesNotExist:
                    p = Profile(user=u, verified=True)
                    p.save()

                teacher_group.user_set.add(u)
                p.centers.add(north_campus)

            except User.DoesNotExist:
                username = email.split('@')[0]
                u = User(username=username, email=email, first_name=first_name, last_name=last_name)
                u.set_password('north')
                u.save()
                teacher_group.user_set.add(u)
                p = Profile(user=u, verified=True)
                p.save()
                p.centers.add(north_campus)
        else:
            print('--', line)

    for line in part_time.splitlines():
        m = re.match(r'''^([a-zA-Z- ]+) ([a-zA-Z- ]+) \<([a-zA-Z0-9.]+\@\w+\.\w+)\>.*$''', line)
        if m:
            first_name, last_name, email = m.group(1), m.group(2), m.group(3)
            #print(m.group(1), m.group(2), m.group(3))
            try:
                u = User.objects.get(email=email)
                if not u.first_name or not u.last_name :
                    u.first_name = first_name
                    u.last_name = last_name
                    u.save()

                try:
                    p = u.profile
                    if not p.verified:
                        p.verified = True
                        p.save()
                except Profile.DoesNotExist:
                    p = Profile(user=u, verified=True)
                    p.save()

                sub_group.user_set.add(u)
                p.centers.add(north_campus)

            except User.DoesNotExist:
                username = email.split('@')[0]
                u = User(username=username, email=email, first_name=first_name, last_name=last_name)
                u.set_password('north')
                u.save()
                sub_group.user_set.add(u)
                p = Profile(user=u, verified=True)
                p.save()
                p.centers.add(north_campus)
        else:
            print('--', line)

class Command(BaseCommand):
    help = 's2c2 cron to copy staff schedule one week ahead based on the template base date.'

    def handle(self, *args, **options):
        import_users()