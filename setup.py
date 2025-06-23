#!/usr/bin/env python
# TODO: remove this and replace with setup.cfg?

import codecs
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import os


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def package_files(*directories):
    paths = []
    for directory in directories:
        for (path, _, filenames) in os.walk(directory):
            for filename in filenames:
                  paths.append(os.path.join(path, filename))
    return paths


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='factorio-draftsman',
    version = get_version("draftsman/_version.py"),
    author='redruin1',
    description='A complete, well-tested, and up-to-date module to manipulate Factorio blueprint strings. Compatible with mods.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["factorio", "blueprint", "string"],
    url='https://github.com/redruin1/factorio-draftsman',
    packages=[
        'draftsman', 
        'draftsman.classes', 
        'draftsman.classes.mixins',
        'draftsman.environment',
        'draftsman.data',
        'draftsman.prototypes'
    ],
    package_data = {
        'draftsman': package_files("draftsman/factorio-data", "draftsman/compatibility", "draftsman/data")
    },
    include_package_data = True,
    install_requires = [
        "attrs >= 25.3.0",
        "cattrs >= 24.1.3",
        "lupa >= 2.0",
        "GitPython >= 3.1.43",
        "typing",
        "typing_extensions; python_version < '3.8'",
        "thefuzz",
    ],
    entry_points = {
        'console_scripts': [
                #'draftsman-update = draftsman.env:main'
                'draftsman = draftsman.environment.script:main'
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        # "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ]
)
