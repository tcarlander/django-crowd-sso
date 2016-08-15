from setuptools import setup

setup(
    name='django-crowd',
    version='0.47',
    packages=['crowd', ],
    install_requires=['django','requests'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
