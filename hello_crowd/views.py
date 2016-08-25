from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from crowd.backends import import_users_from_email_list
from hello_crowd.form import UsersForm


def hello_view(request):
    try:
        print(request.user)
    except AttributeError:
        print('No one')
    return HttpResponse('Hello', content_type='text/plain')


@login_required(login_url='/admin/login/')
def hello_forced_login(request):
    return HttpResponse('Hello ' + request.user.email, content_type='text/plain')


def make_this_list(request):
    if request.method == 'POST':
        form = UsersForm(request.POST)
        if form.is_valid():
            email_list = form.cleaned_data['email_list']

            emails = email_list.split()
            FoundOrAdded, NotFound = import_users_from_email_list(emails)
            print("Added")
            for user in FoundOrAdded:
                print(user)
            print("NotFound")
            for email in NotFound:
                print(email)
    else:
        form = UsersForm()

    return render(request, 'userimport.html', {'form': form})
