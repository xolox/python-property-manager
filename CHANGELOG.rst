Changelog
=========

The purpose of this document is to list all of the notable changes to this
project. The format was inspired by `Keep a Changelog`_. This project adheres
to `semantic versioning`_.

.. contents::
   :local:

.. _Keep a Changelog: http://keepachangelog.com/
.. _semantic versioning: http://semver.org/

`Release 2.3.1`_ (2018-05-19)
-----------------------------

Minor bug fix release to sort the property names in the overview appended to
class docstrings (I'm not sure what the implicit order was but it definitely
wasn't alphabetical :-p).

.. _Release 2.3.1: https://github.com/xolox/python-property-manager/compare/2.3...2.3.1

`Release 2.3`_ (2018-04-27)
---------------------------

- Added ``property_manager.sphinx`` module to automatically generate boilerplate documentation.
- Added ``license`` and removed ``test_suite`` key in ``setup.py`` script.
- Include documentation in source distributions.
- Change Sphinx documentation theme.
- Added this changelog.

.. _Release 2.3: https://github.com/xolox/python-property-manager/compare/2.2...2.3

`Release 2.2`_ (2017-06-29)
---------------------------

- Decomposed ``__repr__()`` into property selection and rendering functionality.
- Added Python 3.6 to tested and supported versions.
- Properly documented logging configuration.
- Switched Sphinx theme (default → classic).
- Refactored ``setup.py`` script and ``Makefile``:

  - Added wheel distributions (``setup.cfg``).
  - Fixed code style checks.

.. _Release 2.2: https://github.com/xolox/python-property-manager/compare/2.1...2.2

`Release 2.1`_ (2016-06-15)
---------------------------

Remove fancy but superfluous words from ``DYNAMIC_PROPERTY_NOTE`` :-).

.. _Release 2.1: https://github.com/xolox/python-property-manager/compare/2.0...2.1

`Release 2.0`_ (2016-06-15)
---------------------------

Easy to use ``PropertyManager`` object hashing and comparisons.

.. _Release 2.0: https://github.com/xolox/python-property-manager/compare/1.6...2.0

`Release 1.6`_ (2016-06-01)
---------------------------

Support for setters, deleters and logging.

.. _Release 1.6: https://github.com/xolox/python-property-manager/compare/1.5...1.6

`Release 1.5`_ (2016-06-01)
---------------------------

- Added ``set_property()`` and ``clear_property()`` functions.
- Added Python 3.5 to tested and supported versions.
- Rearranged class variables and their documentation (I'm still getting up to
  speed with Sphinx, have been doing so for years, probably I'll still be
  learning new things a few years from now :-).

.. _Release 1.5: https://github.com/xolox/python-property-manager/compare/1.4...1.5

`Release 1.4`_ (2016-05-31)
---------------------------

- Only inject usage notes when applicable.
- Start using the ``humanfriendly.sphinx`` module.

.. _Release 1.4: https://github.com/xolox/python-property-manager/compare/1.3...1.4

`Release 1.3`_ (2015-11-25)
---------------------------

Support for properties whose values are based on environment variables.

.. _Release 1.3: https://github.com/xolox/python-property-manager/compare/1.2...1.3

`Release 1.2`_ (2015-10-06)
---------------------------

Made it possible to opt out of usage notes.

.. _Release 1.2: https://github.com/xolox/python-property-manager/compare/1.1.1...1.2

`Release 1.1.1`_ (2015-10-04)
-----------------------------

- Made ``repr()`` render only properties of subclasses.
- Removed indentation from doctest formatted code samples in readme.

.. _Release 1.1.1: https://github.com/xolox/python-property-manager/compare/1.1...1.1.1

`Release 1.1`_ (2015-10-04)
---------------------------

- Documented similar projects and distinguishing features.
- Improved the structure of the documentation.

.. _Release 1.1: https://github.com/xolox/python-property-manager/compare/1.0.1...1.1

`Release 1.0.1`_ (2015-10-04)
-----------------------------

- Improved usage notes of dynamically constructed subclasses.
- Added PyPI trove classifiers to ``setup.py`` script.
- Added Travis CI configuration.

.. _Release 1.0.1: https://github.com/xolox/python-property-manager/compare/1.0...1.0.1

`Release 1.0`_ (2015-10-04)
---------------------------

The initial commit and release. Relevant notes from the readme:

The `property-manager` package came into existence as a submodule of my
executor_ package where I wanted to define classes with a lot of properties
that had a default value which was computed on demand but also needed to
support assignment to easily override the default value.

Since I created that module I'd wanted to re-use it in a couple of other
projects I was working on, but adding an `executor` dependency just for the
`property_manager` submodule felt kind of ugly.

This is when I decided that it was time for the `property-manager` package to
be created. When I extracted the submodule from `executor` I significantly
changed its implementation (making the code more robust and flexible) and
improved the tests, documentation and coverage in the process.

.. _Release 1.0: https://github.com/xolox/python-property-manager/tree/1.0
.. _executor: https://executor.readthedocs.io/en/latest/
