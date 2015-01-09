from django.http import HttpResponse
from django.shortcuts import render


def dummy(request):
    return HttpResponse('Please override.')
    # return render(request, 'snippet/command_form.jinja2')