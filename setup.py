#!/usr/bin/env python

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


# def _setup_factorio_environment():
#       from draftsman.env import update
#       update() # verbose = True


# class PostDevelopCommand(develop):
#       """Post-installation for development mode."""
#       def run(self):
#             develop.run(self)
#             self.execute(_setup_factorio_environment, (),
#                          msg = "Setting up the Factorio Envrionment...")
            

# class PostInstallCommand(install):
#       """Post-installation for installation mode."""
#       def run(self):
#             install.run(self)
#             self.execute(_setup_factorio_environment, (),
#                          msg = "Setting up the Factorio Envrionment...")

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='factorio-draftsman',
      version = get_version("draftsman/_version.py"),
      author='redruin1',
      description='Create and modify Factorio blueprint strings.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/redruin1/factorio_blueprint_tools',
      packages=[
            'draftsman', 
            'draftsman.classes', 
            'draftsman.classes.mixins',
            'draftsman.data',
            'draftsman.prototypes'
      ],
      package_data = {
            'draftsman': 
                  package_files(
                        "draftsman/factorio-data",
                        "draftsman/compatibility",
                  )
      },
      include_package_data = True,
      install_requires = [
            "schema >= 0.7.5",
            "lupa >= 1.10",
            "six >= 1.16.0",
            "typing",
            "importlib-resources; python_version < '3.7'",
            "enum34; python_version < '3.4'",
            "future; python_version < '3.0'",
            "unittest2 >= 1.1.0; python_version < '3.0'",
      ],
      entry_points = {
            'console_scripts': [
                  'draftsman-update = draftsman.env:main'
            ]
      },
      classifiers=[
            "Development Status :: 4 - Beta",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Intended Audience :: Developers",
            "Intended Audience :: End Users/Desktop",
            "Operating System :: OS Independent",
            "License :: OSI Approved :: MIT License"
      ]
)