#!/usr/bin/env python
"""Setup config file."""

from os import path

from setuptools import find_packages, setup


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# PyOpenGL==3.1.6
# scipy==1.9.0
setup(
    name='FramesViewer',
    version='0.1.0',
    packages=find_packages(exclude=['tests']),

    install_requires=[

        'numpy',
        'PyOpenGL',
        'scipy',
    ],


    author='Antoine Pirrone',
    author_email='todo',
    url='https://github.com/apirrone/FramesViewer',

    description='FramesViewer',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
