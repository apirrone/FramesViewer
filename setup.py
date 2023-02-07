#!/usr/bin/env python
"""Setup config file."""

from os import path

from setuptools import find_packages, setup


here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# PyOpenGL==3.1.6
# scipy==1.9.0
setup(
    name="FramesViewer",
    version="1.0.1",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "numpy",
        "PyOpenGL",
        "scipy",
        "pywavefront"
    ],
    author="Antoine Pirrone",
    author_email="antoine.pirrone@gmail.com",
    url="https://github.com/apirrone/FramesViewer",
    description="A simple live 6D frames viewer (and more)",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
