from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from user.models import UserProfile


def user_monkey_patch():

    def get_name(self):
        return self.get_full_name() or self.username

    def get_link(self):
        return reverse('cal:staff', kwargs={'uid': self.id})

    def get_user_profile(self):
        return UserProfile(self)

    User.add_to_class("get_name", get_name)
    User.add_to_class("get_link", get_link)
    User.add_to_class("user_profile", get_user_profile)


user_monkey_patch()