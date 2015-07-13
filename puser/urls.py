from django.conf.urls import patterns, url
# import circle.views
from puser import views

urlpatterns = patterns(
    "",
    url(r"^login/$", views.LoginView.as_view(), name="account_login"),
    url(r"^logout/$", views.logout, name="account_logout"),
    url(r"^signup/$", views.OnboardWizard.as_view(), name="account_signup"),

    # todo: allow other people view account
    url(r"^$", views.UserView.as_view(), name="account_view"),
    url(r"^(?P<pk>\d+)/$", views.UserView.as_view(), name="account_view"),

    url(r"^edit/$", views.UserEdit.as_view(), name="account_edit"),
    url(r"^picture/$", views.UserPicture.as_view(), name="account_picture"),

    # url(r"^circle/$", circle.views.ManageCircleView.as_view(), name="account_circle"),
    # url(r"^favorite/$", circle.views.ManageFavoriteView.as_view(), name="account_favorite"),

    url(r"^api/email/(?P<email>\S+@\S+)/$", views.APIGetByEmail.as_view(), name="account_api_by_email"),
)
