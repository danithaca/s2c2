from django.http import HttpResponse


def dummy(request, message='Please override.'):
    return HttpResponse(message)
    # return render(request, 'snippet/command_form.jinja2')