from distutils.core import setup

setup(
    name='django-crowd',
    version='0.46',
    packages=['crowd', ],
    install_requires=['requests'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
