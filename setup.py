import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='wfp-django-crowd',
    version='0.53',
    description='Atlassina Crowd integration for Django',
    packages=['crowd', ],
    install_requires=['django', 'requests', 'simplejson', 'pandoc'],
    url='https://github.com/WFP-BKK/django-crowd',
    author='Tobias Carlander',
    author_email='tobias.carlander@wfp.org',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Creative Commons Attribution-Noncommercial-Share Alike license',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    long_description=README,

    keywords='django crowd users',

)
