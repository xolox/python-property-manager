#!/usr/bin/env python

"""Setup script for the `property-manager` package."""

# Author: Peter Odding <peter@peterodding.com>
# Last Change: June 14, 2016
# URL: https://property-manager.readthedocs.org

# Standard library modules.
import codecs
import os
import re

# De-facto standard solution for Python packaging.
from setuptools import find_packages, setup


def get_contents(*args):
    """Get the contents of a file relative to the source distribution directory."""
    with codecs.open(get_absolute_path(*args), 'r', 'UTF-8') as handle:
        return handle.read()


def get_version(*args):
    """Extract the version number from a Python module."""
    contents = get_contents(*args)
    metadata = dict(re.findall('__([a-z]+)__ = [\'"]([^\'"]+)', contents))
    return metadata['version']


def get_absolute_path(*args):
    """Transform relative pathnames into absolute pathnames."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)


setup(name="property-manager",
      version=get_version('property_manager', '__init__.py'),
      description=("Useful property variants for Python programming (required"
                   " properties, writable properties, cached properties, etc)"),
      long_description=get_contents('README.rst'),
      url='https://property-manager.readthedocs.org',
      author="Peter Odding",
      author_email='peter@peterodding.com',
      packages=find_packages(),
      install_requires=[
          'humanfriendly >= 1.44.7',
          'verboselogs >= 1.1',
      ],
      tests_require=[
          'coloredlogs >= 5.0',
      ],
      test_suite='property_manager.tests',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Documentation :: Sphinx',
          'Topic :: Software Development',
          'Topic :: Software Development :: Documentation',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ])
