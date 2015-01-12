from django.http import HttpResponse
from django.shortcuts import render


def dummy(request, message='Please override.'):
    return HttpResponse(message)
    # return render(request, 'snippet/command_form.jinja2')