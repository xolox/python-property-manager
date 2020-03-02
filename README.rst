property-manager: Useful property variants for Python programming
=================================================================

.. image:: https://travis-ci.org/xolox/python-property-manager.svg?branch=master
   :target: https://travis-ci.org/xolox/python-property-manager

.. image:: https://coveralls.io/repos/github/xolox/python-property-manager/badge.svg?branch=master
   :target: https://coveralls.io/github/xolox/python-property-manager?branch=master

The `property-manager` package defines several custom property_ variants for
Python programming including required properties, writable properties, cached
properties, etc. It's currently tested on Python 2.7, 3.5, 3.6, 3.7, 3.8 and
PyPy. For usage instructions please refer to the documentation_.

.. contents::
   :local:

Status
------

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

Installation
------------

The `property-manager` package is available on PyPI_ which means installation
should be as simple as:

.. code-block:: sh

   $ pip install property-manager

There's actually a multitude of ways to install Python packages (e.g. the `per
user site-packages directory`_, `virtual environments`_ or just installing
system wide) and I have no intention of getting into that discussion here, so
if this intimidates you then read up on your options before returning to these
instructions ;-).

Usage
-----

This section shows how to use the most useful property subclasses. Please refer
to the documentation_ for more detailed information.

.. contents::
   :local:

Writable properties
~~~~~~~~~~~~~~~~~~~

Writable properties with a computed default value are easy to create using the
writable_property_ decorator:

.. code-block:: python

   from random import random
   from property_manager import writable_property

   class WritablePropertyDemo(object):

       @writable_property
       def change_me(self):
           return random()

First let's see how the computed default value behaves:

>>> instance = WritablePropertyDemo()
>>> print(instance.change_me)
0.13692489329941815
>>> print(instance.change_me)
0.8664002331885933

As you can see the value is recomputed each time. Now we'll assign it a value:

>>> instance.change_me = 42
>>> print(instance.change_me)
42

From this point onwards `change_me` will be the number 42_ and it's impossible
to revert back to the computed value:

>>> delattr(instance, 'change_me')
Traceback (most recent call last):
  File "property_manager/__init__.py", line 584, in __delete__
    raise AttributeError(msg % (obj.__class__.__name__, self.__name__))
AttributeError: 'WritablePropertyDemo' object attribute 'change_me' is read-only

If you're looking for a property that supports both assignment and deletion
(clearing the assigned value) you can use mutable_property_.

Required properties
~~~~~~~~~~~~~~~~~~~

The required_property_ decorator can be used to create required properties:

.. code-block:: python

   from property_manager import PropertyManager, required_property

   class RequiredPropertyDemo(PropertyManager):

       @required_property
       def important(self):
           """A very important attribute."""

What does it mean for a property to be required? Let's create an instance of
the class and find out:

>>> instance = RequiredPropertyDemo()
Traceback (most recent call last):
  File "property_manager/__init__.py", line 131, in __init__
    raise TypeError("%s (%s)" % (msg, concatenate(missing_properties)))
TypeError: missing 1 required argument (important)

So the constructor of the class raises an exception when the property hasn't
been given a value. We can give the property a value by providing keyword
arguments to the constructor:

>>> instance = RequiredPropertyDemo(important=42)
>>> print(instance)
RequiredPropertyDemo(important=42)

We can also assign a new value to the property:

>>> instance.important = 13
>>> print(instance)
RequiredPropertyDemo(important=13)

Cached properties
~~~~~~~~~~~~~~~~~

Two kinds of cached properties are supported, we'll show both here:

.. code-block:: python

   from random import random
   from property_manager import cached_property, lazy_property

   class CachedPropertyDemo(object):

       @cached_property
       def expensive(self):
           print("Calculating expensive property ..")
           return random()

       @lazy_property
       def non_idempotent(self):
           print("Calculating non-idempotent property ..")
           return random()

The properties created by the cached_property_ decorator compute the
property's value on demand and cache the result:

>>> instance = CachedPropertyDemo()
>>> print(instance.expensive)
Calculating expensive property ..
0.763863180683
>>> print(instance.expensive)
0.763863180683

The property's cached value can be invalidated in order to recompute its value:

>>> del instance.expensive
>>> print(instance.expensive)
Calculating expensive property ..
0.396322737214
>>> print(instance.expensive)
0.396322737214

Now that you understand cached_property_, explaining lazy_property_ is very
simple: It simply doesn't support invalidation of cached values! Here's how
that works in practice:

>>> instance.non_idempotent
Calculating non-idempotent property ..
0.27632566561900895
>>> instance.non_idempotent
0.27632566561900895
>>> del instance.non_idempotent
Traceback (most recent call last):
  File "property_manager/__init__.py", line 499, in __delete__
    raise AttributeError(msg % (obj.__class__.__name__, self.__name__))
AttributeError: 'CachedPropertyDemo' object attribute 'non_idempotent' is read-only
>>> instance.non_idempotent
0.27632566561900895

Properties based on environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The constructor of the custom_property_ class (and its subclasses) accepts the
keyword argument `environment_variable` which can be provided to get the
property's value from the environment:

.. code-block:: python

   from random import random
   from property_manager import mutable_property

   class EnvironmentPropertyDemo(object):

       @mutable_property(environment_variable='WHATEVER_YOU_WANT')
       def environment_based(self):
           return 'some-default-value'

By default the property's value is computed as expected:

>>> instance = EnvironmentPropertyDemo()
>>> print(instance.environment_based)
some-default-value

When the environment variable is set it overrides the computed value:

>>> os.environ['WHATEVER_YOU_WANT'] = '42'
>>> print(instance.environment_based)
42

Assigning a value to the property overrides the value from the environment:

>>> instance.environment_based = '13'
>>> print(instance.environment_based)
13

Deleting the property clears the assigned value so that the property falls back
to the environment:

>>> delattr(instance, 'environment_based')
>>> print(instance.environment_based)
42

If we now clear the environment variable as well then the property falls back
to the computed value:

>>> os.environ.pop('WHATEVER_YOU_WANT')
'42'
>>> print(instance.environment_based)
some-default-value

Support for setters and deleters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All of the custom property classes support setters and deleters just like
Python's ``property`` decorator does.

The `PropertyManager` class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you define a class that inherits from the PropertyManager_ class the
following behavior is made available to your class:

- Required properties raise an exception if they're not set.

- The values of writable properties can be set by passing
  keyword arguments to the constructor of your class.

- The `repr()` of your objects will render the name of the class and the names
  and values of all properties. Individual properties can easily be excluded
  from the `repr()` output.

- The `clear_cached_properties()`_ method can be used to invalidate the cached
  values of all cached properties at once.

Additionally you can use the property_manager.sphinx_ module as a Sphinx
extension to automatically generate boilerplate documentation that provides an
overview of base classes, properties, public methods and special methods.

Similar projects
----------------

The Python Package Index contains quite a few packages that provide custom
properties with similar semantics:

`cached-property <https://pypi.python.org/pypi/cached-property>`_
 My personal favorite until I wrote my own :-). This package provides several
 cached property variants. It supports threading and time based cache
 invalidation which `property-manager` doesn't support.

`lazy-property <https://pypi.python.org/pypi/lazy-property>`_
 This package provides two cached property variants: a read only property and
 a writable property. Both variants cache computed values indefinitely.

`memoized-property <https://pypi.python.org/pypi/memoized-property>`_
 This package provides a single property variant which simply caches computed
 values indefinitely.

`property-caching <https://pypi.python.org/pypi/property-caching>`_
 This package provides several cached property variants supporting class
 properties, object properties and cache invalidation.

`propertylib <https://pypi.python.org/pypi/propertylib>`_
 This package uses metaclasses to implement an alternative syntax for defining
 computed properties. It defines several property variants with semantics that
 are similar to those defined by the `property-manager` package.

`rwproperty <https://pypi.python.org/pypi/rwproperty>`_
 This package implements computed, writable properties using an alternative
 syntax to define the properties.

Distinguishing features
~~~~~~~~~~~~~~~~~~~~~~~

Despite all of the existing Python packages discussed above I decided to create
and publish the `property-manager` package because it was fun to get to know
Python's `descriptor protocol`_ and I had several features in mind I couldn't
find anywhere else:

- A superclass that sets writable properties based on constructor arguments.

- A superclass that understands required properties and raises a clear
  exception if a required property is not properly initialized.

- Clear disambiguation between lazy properties (whose computed value is cached
  but cannot be invalidated because it would compromise internal state) and
  cached properties (whose computed value is cached but can be invalidated to
  compute a fresh value).

- An easy way to quickly invalidate all cached properties of an object.

- An easy way to change the semantics of custom properties, e.g. what if the
  user wants a writable cached property? With `property-manager` it is trivial
  to define new property variants by combining existing semantics:

  .. code-block:: python

     from property_manager import cached_property

     class WritableCachedPropertyDemo(object):

         @cached_property(writable=True)
         def expensive_overridable_attribute(self):
             """Expensive calculations go here."""

  The example above creates a new anonymous class and then immediately uses
  that to decorate the method. We could have given the class a name though:

  .. code-block:: python

     from property_manager import cached_property

     writable_cached_property = cached_property(writable=True)

     class WritableCachedPropertyDemo(object):

         @writable_cached_property
         def expensive_overridable_attribute(self):
             """Expensive calculations go here."""

  By giving the new property variant a name it can be reused. We can go one
  step further and properly document the new property variant:

  .. code-block:: python

     from property_manager import cached_property

     class writable_cached_property(cached_property):

         """A cached property that supports assignment."""

         writable = True

     class WritableCachedPropertyDemo(object):

         @writable_cached_property
         def expensive_overridable_attribute(self):
             """Expensive calculations go here."""

  I've used computed properties for years in Python and over those years I've
  learned that different Python projects have different requirements from
  custom property variants. Defining every possible permutation up front is
  madness, but I think that the flexibility with which the `property-manager`
  package enables adaptation gets a long way. This was the one thing that
  bothered me the most about all of the other Python packages that implement
  property variants: They are not easily adapted to unanticipated use cases.

Contact
-------

The latest version of `property-manager` is available on PyPI_ and GitHub_. The
documentation is hosted on `Read the Docs`_ and includes a changelog_. For bug
reports please create an issue on GitHub_. If you have questions, suggestions,
etc. feel free to send me an e-mail at `peter@peterodding.com`_.

License
-------

This software is licensed under the `MIT license`_.

© 2020 Peter Odding.


.. External references:
.. _42: https://en.wikipedia.org/wiki/42_(number)#The_Hitchhiker.27s_Guide_to_the_Galaxy
.. _cached_property: https://property-manager.readthedocs.io/en/latest/api.html#property_manager.cached_property
.. _changelog: https://property-manager.readthedocs.io/en/latest/changelog.html
.. _clear_cached_properties(): https://property-manager.readthedocs.io/en/latest/api.html#property_manager.PropertyManager.clear_cached_properties
.. _custom_property: https://property-manager.readthedocs.io/en/latest/api.html#property_manager.custom_property
.. _descriptor protocol: https://docs.python.org/2/howto/descriptor.html
.. _documentation: https://property-manager.readthedocs.io
.. _executor: https://executor.readthedocs.org/en/latest/
.. _GitHub: https://github.com/xolox/python-property-manager
.. _lazy_property: https://property-manager.readthedocs.io/en/latest/api.html#property_manager.lazy_property
.. _MIT license: http://en.wikipedia.org/wiki/MIT_License
.. _mutable_property: https://property-manager.readthedocs.io/en/latest/api.html#property_manager.mutable_property
.. _per user site-packages directory: https://www.python.org/dev/peps/pep-0370/
.. _peter@peterodding.com: peter@peterodding.com
.. _property: https://docs.python.org/2/library/functions.html#property
.. _property_manager.sphinx: https://property-manager.readthedocs.io/en/latest/api.html#property_manager.sphinx
.. _PropertyManager: https://property-manager.readthedocs.io/en/latest/api.html#property_manager.PropertyManager
.. _PyPI: https://pypi.python.org/pypi/property-manager
.. _Read the Docs: https://property-manager.readthedocs.io
.. _required_property: https://property-manager.readthedocs.io/en/latest/api.html#property_manager.required_property
.. _virtual environments: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _writable_property: https://property-manager.readthedocs.io/en/latest/api.html#property_manager.writable_property
