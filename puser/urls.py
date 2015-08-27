from django.conf.urls import patterns, url
from puser import views

urlpatterns = patterns(
    "",
    url(r"^login/$", views.LoginView.as_view(), name="account_login"),
    url(r"^logout/$", views.logout, name="account_logout"),
    url(r"^password/$", views.SimpleChangePasswordView.as_view(), name="account_password"),
    # url(r"^signup/$", views.OnboardWizard.as_view(), name="account_signup"),
    url(r"^signup/$", views.SignupView.as_view(), name="account_signup"),

    url(r"^onboard/about/$", views.OnboardAbout.as_view(), name="onboard_start"),
    # url(r"^onboard/signup/$", views.OnboardSignup.as_view(), name="onboard_signup"),
    url(r"^onboard/about/$", views.OnboardAbout.as_view(), name="onboard_about"),
    url(r"^onboard/profile/$", views.OnboardProfile.as_view(), name="onboard_profile"),
    url(r"^onboard/personal/$", views.OnboardPersonalCircle.as_view(), name="onboard_personal"),
    url(r"^onboard/public/$", views.OnboardPublicCircle.as_view(), name="onboard_public"),
    url(r"^onboard/picture/$", views.OnboardPicture.as_view(), name="onboard_picture"),

    # todo: allow other people view account
    url(r"^$", views.UserView.as_view(), name="account_view"),
    url(r"^(?P<pk>\d+)/$", views.UserView.as_view(), name="account_view"),

    url(r"^edit/$", views.UserEdit.as_view(), name="account_edit"),
    url(r"^picture/$", views.UserPicture.as_view(), name="account_picture"),

    # url(r"^circle/$", circle.views.ManageCircleView.as_view(), name="account_circle"),
    # url(r"^favorite/$", circle.views.ManageFavoriteView.as_view(), name="account_favorite"),

    url(r"^api/email/(?P<email>\S+@\S+)/$", views.APIGetByEmail.as_view(), name="account_api_by_email"),
)
