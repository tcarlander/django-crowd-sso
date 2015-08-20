from django.conf.urls import url
from authentication.views import Login, Logout

urlpatterns = [
    url(r'^in/$', Login.as_view(), name='login'),
    url(r'^out/$', Logout.as_view(), name='logout'),
    ]

