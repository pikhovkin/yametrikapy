#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='yametrikapy',
    version=__import__('yametrikapy').__version__,
    description=open('DESCRIPTION').read(),
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
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages()
)

