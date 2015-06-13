from django.conf.urls import patterns, url
import circle.views
from puser import views

urlpatterns = patterns(
    "",
    url(r"^login/$", views.LoginView.as_view(), name="account_login"),
    url(r"^logout/$", views.logout, name="account_logout"),
    url(r"^signup/$", views.OnboardWizard.as_view(), name="account_signup"),
    url(r"^view/$", views.UserView.as_view(), name="account_view"),
    url(r"^edit/$", views.UserEditView.as_view(), name="account_edit"),

    url(r"^circle/$", circle.views.ManageCircleView.as_view(), name="account_circle"),
    url(r"^favorite/$", circle.views.ManageFavoriteView.as_view(), name="account_favorite"),

    # url(r"^password/reset/$", views.PasswordResetView.as_view(), name="account_password_reset"),
)
