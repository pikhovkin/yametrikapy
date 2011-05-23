#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name='yametrikapy',
    version=__import__('yametrikapy').__version__,
    description=read('DESCRIPTION'),
    license='MIT',
    keywords='yandex metrika api',
    author='Sergey Pikhovkin',
    author_email='s@pikhovkin.ru',
    maintainer='Sergey Pikhovkin',
    maintainer_email='s@pikhovkin.ru',
    url='https://github.com/pikhovkin/yametrikapy/',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
    long_description=read('README.rst'),
    packages=find_packages()
)

