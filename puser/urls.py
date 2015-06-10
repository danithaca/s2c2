from account.views import SignupView, ChangePasswordView, PasswordResetTokenView
from django.conf.urls import patterns, url
from puser import views

urlpatterns = patterns(
    "",
    url(r"^signup/$", SignupView.as_view(), name="account_signup"),
    url(r"^login/$", views.LoginView.as_view(), name="account_login"),
    url(r"^logout/$", views.logout, name="account_logout"),
    # url(r"^confirm_email/(?P<key>\w+)/$", ConfirmEmailView.as_view(), name="account_confirm_email"),
    url(r"^password/$", ChangePasswordView.as_view(), name="account_password"),
    url(r"^password/reset/$", views.PasswordResetView.as_view(), name="account_password_reset"),
    url(r"^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$", PasswordResetTokenView.as_view(), name="account_password_reset_token"),
    # url(r"^settings/$", SettingsView.as_view(), name="account_settings"),
    # url(r"^delete/$", DeleteView.as_view(), name="account_delete"),
)
