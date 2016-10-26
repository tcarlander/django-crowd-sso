django-crowd
============
Simple Atlasian CROWD authentication backend for Django with SSO support



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
    'validation':'10.11.40.34',                             # The ipaddress the Crowd server is responding to
    'sso': False,
}
```

Add `crowd.CrowdBackend` in your `AUTHENTICATION_BACKENDS` settings list.
Put it first so that password are only kept in CROWD:

```
AUTHENTICATION_BACKENDS = (
    'crowd.backends.CrowdBackend'
    'django.contrib.auth.backends.ModelBackend',
)
```


Add     'crowd.middleware.CookieMiddleware' to the Middleware 


AUTHENTICATION_BACKENDS list to make sure you always start with crowd authentication before falling over to
a local account.

simple test:
`./manage.py test`

Tox test:
`tox`

test currenly does not cover the SSO

**New For version 0.52**

Added disalowed emails to the import first version hardcoded @wfp.org, will be a setting in future

any email with @wfp.org but not in crowd will be in the dissalowed list
 
example of use

* User with email a@b.c is already user 'a' in the local db as a django created user
* User with email b@c.c is already user 'b' in the local db as a imported user from Crowd
* User with email c@a.b is no already user in the local db but exists in Crowd so it will be imported as user 'b'
* User with email d@e.f is not in local db nor in Crowd
* User with email e@wfp.org is on dissalowed list 

```
from crowd.backends import import_users_from_email_list

        emails = ["a@b.c", "b@c.c", "c@a.b", "d@e.f","e@wfp.org"]
        added_or_found, not_found, not_alowed = import_users_from_email_list(emails)
        print(added_or_found)
        print(not_found)
        print(not_allowed)
```
Resulting printout:
```
['a','b','c']

['d@e.f']

['e@wfp.org']
```


Credits:
========

Originally written for Django v1.3 by Konstantin J. Volkov <konstantin-j-volkov@yandex.ru> at 12.07.2012

Refactored, put together and tested with Django v1.4 by Grigoriy Beziuk <gbezyuk@gmail.com> at 27.08.2012

Refactored, updated for Django 1.9 and added SSO and other features by Tobias Carlander <tobias.carlander@wfp.org> at 2015/03/25
