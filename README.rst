property-manager: Useful property variants for Python programming
=================================================================

.. image:: https://travis-ci.org/xolox/python-property-manager.svg?branch=master
   :target: https://travis-ci.org/xolox/python-property-manager

.. image:: https://coveralls.io/repos/xolox/python-property-manager/badge.png?branch=master
   :target: https://coveralls.io/r/xolox/python-property-manager?branch=master

The `property-manager` package defines several custom property_ variants for
Python programming including required properties, writable properties, cached
properties, etc. It's currently tested on Python 2.6, 2.7, 3.4 and PyPy. For
usage instructions please refer to the documentation_.

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

Here's how you create a writable property with a computed default value:

.. code-block:: python

   from random import random
   from property_manager import PropertyManager, writable_property

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

From this point onwards `change_me` will be the number 42.

Required properties
~~~~~~~~~~~~~~~~~~~

Here's how you create a required property:

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

The properties created by the `cached_property` decorator compute the
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

Now that you understand `cached_property`, explaining `lazy_property` is very
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

The `PropertyManager` class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you define a class that inherits from the `PropertyManager` class the
following behavior is made available to your class:

- Required properties raise an exception if they're not set.

- The values of writable properties can be set by passing
  keyword arguments to the constructor of your class.

- The `repr()` of your objects will render the name of the class and the names
  and values of all properties. Individual properties can easily be excluded
  from the `repr()` output.

- The `clear_cached_properties()` method can be used to invalidate the cached
  values of all cached properties at once.

Contact
-------

The latest version of `property-manager` is available on PyPI_ and GitHub_. The
documentation is hosted on `Read the Docs`_. For bug reports please create an
issue on GitHub_. If you have questions, suggestions, etc. feel free to send me
an e-mail at `peter@peterodding.com`_.

License
-------

This software is licensed under the `MIT license`_.

© 2015 Peter Odding.


.. External references:
.. _documentation: https://property-manager.readthedocs.org
.. _executor: https://executor.readthedocs.org/en/latest/
.. _GitHub: https://github.com/xolox/python-property-manager
.. _MIT license: http://en.wikipedia.org/wiki/MIT_License
.. _per user site-packages directory: https://www.python.org/dev/peps/pep-0370/
.. _peter@peterodding.com: peter@peterodding.com
.. _property: https://docs.python.org/2/library/functions.html#property
.. _PyPI: https://pypi.python.org/pypi/property-manager
.. _Read the Docs: https://property-manager.readthedocs.org
.. _virtual environments: http://docs.python-guide.org/en/latest/dev/virtualenvs/
