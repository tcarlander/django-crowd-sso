from setuptools import setup

setup(
    name='django-crowd',
    version='0.50',
    packages=['crowd', ],
    install_requires=['django', 'requests', 'simplejson'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
