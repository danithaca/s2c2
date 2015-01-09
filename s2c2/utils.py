from django.http import HttpResponse


def dummy(request):
    return HttpResponse('Please override.')