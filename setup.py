from distutils.core import setup

setup(
    name='django-crowd',
    version='0.45',
    packages=['crowd', ],
    install_requires=[
        "requests",
        "django",
    ],

    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
