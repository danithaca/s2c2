from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.views.generic import FormView


class SignupForm(UserCreationForm):
    pass


class SignupView(FormView):
    template_name = 'user/signup.jinja2'
    form_class = SignupForm
    success_url = '/'

    def form_valid(self, form):
        # this calls SignupForm::UserCreationForm::save()
        form.save()
        # this calls the default FormView::form_valid()
        return super(SignupView, self).form_valid(form)


def signup(request):
    #return SignupView.as_view()
    return render(request, 'user/signup.jinja2')


def login(request):
    return auth_views.login(request, template_name='user/login.jinja2', extra_context={'next': '/'})