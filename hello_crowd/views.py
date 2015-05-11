from django.shortcuts import render
from django.http import HttpResponse, JsonResponse 
from django.contrib.auth.decorators import login_required


# Create your views here.
def hello_view(request):
    try:
        print(request.user)
    except:
        print('Noone')
    return HttpResponse('Hello',content_type='text/plain')

@login_required(login_url='/admin/login/')
def hello_forceLogin(request):
    return HttpResponse('Hello',content_type='text/plain')