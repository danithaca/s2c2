from django.conf.urls import patterns, url
from puser import views

urlpatterns = patterns(
    "",
    url(r"^login/$", views.LoginView.as_view(), name="account_login"),
    url(r"^logout/$", views.logout, name="account_logout"),
    url(r"^signup/$", views.OnboardWizard.as_view(), name="account_signup"),
    # url(r"^password/reset/$", views.PasswordResetView.as_view(), name="account_password_reset"),
)
