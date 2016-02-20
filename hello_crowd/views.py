from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from crowd.backends import import_users
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
            import_users(users)
            for user in users:
                print(user)
            #form.data = form.data.copy()
            #form.data['user_list'] = "Done"
            return render(request, 'userimport.html', {'form': form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UsersForm()

    return render(request, 'userimport.html', {'form': form})