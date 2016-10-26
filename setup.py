from setuptools import setup

setup(
    name='django-crowd',
    version='0.52',
    packages=['crowd', ],
    install_requires=['django', 'requests', 'simplejson'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
