import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'readme.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='django_mailtor',
    version='0.0.28',
    packages=find_packages(),
    include_package_data=True,
    license='GNU License',
    description='A Django app ',
    long_description=README,
    url='https://github.com/cavg/django_mailtor/',
    author='Camilo Verdugo',
    author_email='camilo.verdugo@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: CC',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6.1',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=required,
)
