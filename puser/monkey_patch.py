from django.contrib.auth.models import User


def user_monkey_patch():

    def get_name(self):
        return self.get_full_name() or self.username

    def to_puser(self):
        from puser.models import PUser
        return PUser.from_user(self)

    User.add_to_class("get_name", get_name)
    User.add_to_class("to_puser", to_puser)


user_monkey_patch()