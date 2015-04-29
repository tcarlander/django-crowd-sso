from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'crowdtest.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^accounts/login/$', auth_views.login),
    url(r'^admin/', include(admin.site.urls)),
)

