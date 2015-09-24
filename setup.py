#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'Myrmidon',
    version = '0.5.4',
    description = '2D game framework for rapid development',
    author = 'Fiona Burrows',
    author_email = 'fiona@justfiona.com',
    url = 'http://www.github.com/Fiona/Myrmidon',
    license = 'MIT',
    packages = find_packages(exclude=['tests']),        
    test_suite = 'tests',
    install_requires = [
        'pygame>=1.9.0release',
        'numpy',
        'pyOpenGL',
    ],
)
