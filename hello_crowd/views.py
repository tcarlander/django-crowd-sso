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
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = UsersForm(request.POST)
        if form.is_valid():
            user_list = form.cleaned_data['user_list']

            users = user_list.split()
            added, not_found = import_users_from_email_list(users)
            print("Added")
            for user in added:
                print(user)
            print("NotFound")
            for user in not_found:
                print(user)
            return render(request, 'userimport.html', {'form': form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UsersForm()

    return render(request, 'userimport.html', {'form': form})
