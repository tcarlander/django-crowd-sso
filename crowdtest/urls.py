from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls import include, patterns, url
import hello_crowd.views
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'crowdtest.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$',hello_crowd.views.hello_view),
    url(r'^l$',hello_crowd.views.hello_forceLogin),
    #url(r'^accounts/login/$', auth_views.login),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^admin/', include(admin.site.urls)),
)

