import os
from setuptools import find_packages, setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()


os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-crowd-sso',
    version='0.58',
    description='Atlassian Crowd integration for Django with SSO',
    packages=['crowd'],
    install_requires=['django', 'requests', 'simplejson'],
    url='https://github.com/WFP-BKK/django-crowd-sso',
    author='Tobias Carlander',
    author_email='tobias.carlander@wfp.org',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    long_description=read_md('README.md'),
    keywords='django crowd users authentication sso',
)
