from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


# Create your views here.
def hello_view(request):
    try:
        print(request.user)
    except AttributeError:
        print('No one')
    return HttpResponse('Hello', content_type='text/plain')


@login_required(login_url='/admin/login/')
def hello_forced_login(request):
    return HttpResponse('Hello', content_type='text/plain')
