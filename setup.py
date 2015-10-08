from distutils.core import setup

setup(
    name='django-crowd',
    version='0.46.1',
    packages=['crowd', ],
    install_requires=['django','requests'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
