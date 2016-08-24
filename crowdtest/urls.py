from django.contrib import admin
from django.conf.urls import url
from django.contrib.auth.views import login, logout

import hello_crowd.views

urlpatterns = [
    url(r'^$', hello_crowd.views.hello_view),
    url(r'^l$', hello_crowd.views.hello_forced_login),
    url(r'^logout$', logout),
    url(r'^accounts/login/$', login),
    url(r'^admin/', admin.site.urls),
    url(r'insert_users/$', hello_crowd.views.make_this_list),
]
