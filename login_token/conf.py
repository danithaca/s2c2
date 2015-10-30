from appconf import AppConf
from django.conf import settings


class LoginTokenConfig(AppConf):
    PARAM = 'login_token'
    LENGTH = 64     # maximum is 64