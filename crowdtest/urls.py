from django.contrib import admin
from django.conf.urls import include, patterns, url

import hello_crowd.views

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'crowdtest.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       url(r'^$', hello_crowd.views.hello_view),
                       url(r'^l$', hello_crowd.views.hello_forced_login),
                       # url(r'^accounts/login/$', auth_views.login),
                       (r'^accounts/login/$', 'django.contrib.auth.views.login'),
                       url(r'^admin/', include(admin.site.urls)),
                       )
