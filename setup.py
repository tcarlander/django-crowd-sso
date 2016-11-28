import os
from setuptools import find_packages, setup

#with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
#    README = readme.read()
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
README = "Soon"

setup(
    name='django-crowd-sso',
    version='0.56',
    description='Atlassina Crowd integration for Django with SSO',
    packages=['crowd', ],
    install_requires=['django', 'requests', 'simplejson'],
    url='https://github.com/WFP-BKK/django-crowd-sso',
    author='Tobias Carlander',
    author_email='tobias.carlander@wfp.org',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    long_description=README,
    keywords='django crowd users authentication sso',

)
