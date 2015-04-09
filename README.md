django-crowd
============
Simple Attlasian CROWD authentication backend for Django



Configuration:
==============
Put a CROWD configuration in your `settings.py`:

```
CROWD = {
    'url': 'http://your.crowd.url:port/crowd/rest',         # your CROWD rest API url
    'app_name': 'your-registered-crowd-application-name',   # appname, registered with CROWD
    'password': 'application-password',                     # correct password for provided appname
    'superuser': True,                                      # if set makes CROWD-authorized users superusers;
    'staffuser': True,                                      # BE CAREFUL WITH THIS PARAMETER!
    'validation':'10.11.40.34',                             # The ipaddress the Crowd server is responding to (
}
```

Add `crowd.CrowdBackend` in your `AUTHENTICATION_BACKENDS` settings list.
Put it first so that password are only kept in CROWD:

```
AUTHENTICATION_BACKENDS = (
    # ...
    'crowd.backends.CrowdBackend'
    'django.contrib.auth.backends.ModelBackend',
)
```


Add     'crowd.middleware.CookieMiddleware' to the Middleware 


AUTHENTICATION_BACKENDS list to make sure you always start with crowd authentication before falling over to
a local account.

Credits:
========

Originally written for Django v1.3 by Konstantin J. Volkov <konstantin-j-volkov@yandex.ru> at 12.07.2012

Refactored, put together and tested with Django v1.4 by Grigoriy Beziuk <gbezyuk@gmail.com> at 27.08.2012

Refactored and added SSO by Tobias Carlander <tobias.carlander@wfp.org>
