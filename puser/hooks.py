# from account.hooks import AccountDefaultHookSet
# from django.contrib import messages
#
#
# class AccountHookSet(AccountDefaultHookSet):
#
#     def send_password_reset_email(self, to, ctx):
#         try:
#             super(AccountHookSet, self).send_password_reset_email(to, ctx)
#         except ConnectionRefusedError as e:
#             messages.