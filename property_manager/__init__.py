# Useful property variants for Python programming.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: October 4, 2015
# URL: https://property-manager.readthedocs.org

"""
Useful :class:`property` variants for Python programming.

Introduction
============

The :mod:`property_manager` module defines several :class:`property` variants
that implement Python's `descriptor protocol`_ to provide decorators that turn
methods into computed properties with several additional features.

Custom property types
---------------------

Here's an overview of the predefined property variants and their supported
operations:

==========================  ================  =============  ==========
Variant                     Can be assigned?  Can be reset?  Is cached?
==========================  ================  =============  ==========
:class:`custom_property`      No                No             No
:class:`writable_property`    Yes               No             No
:class:`mutable_property`     Yes               Yes            No
:class:`required_property`    Yes               No             No
:class:`lazy_property`        No                No             Yes
:class:`cached_property`      No                Yes            Yes
==========================  ================  =============  ==========

If you want a different combination of supported options (for example a cached
property that supports assignment) this is also possible, please take a look at
:class:`custom_property.__new__()`.

The following inheritance diagram shows how the predefined :class:`property`
variants relate to each other:

.. inheritance-diagram:: property_manager.custom_property \
                         property_manager.writable_property \
                         property_manager.mutable_property \
                         property_manager.required_property \
                         property_manager.lazy_property \
                         property_manager.cached_property
   :parts: 1

The property manager superclass
-------------------------------

In addition to these :class:`property` variants the :mod:`property_manager`
module also defines a :class:`PropertyManager` class which implements several
related enhancements:

- Keyword arguments to the constructor can be used to set writable properties
  created using any of the :class:`property` variants defined by the
  :mod:`property_manager` module.

- Required properties without an assigned value will cause the constructor
  to raise an appropriate exception (:exc:`~exceptions.TypeError`).

- The :func:`repr()` of :class:`PropertyManager` objects shows the names and
  values of all properties. Individual properties can be omitted from the
  :func:`repr()` output by setting the :attr:`~custom_property.repr` option to
  :data:`False`.

Classes
=======

.. _descriptor protocol: https://docs.python.org/2/howto/descriptor.html
"""

# Standard library modules.
import textwrap

# External dependencies.
from humanfriendly import compact, concatenate, format, pluralize

try:
    # Check if `basestring' is defined (Python 2).
    basestring = basestring
except NameError:
    # Alias basestring to str in Python 3.
    basestring = str

__version__ = '1.1'
"""Semi-standard module versioning."""

NOTHING = object()
"""A unique object instance used to detect missing attributes."""

CUSTOM_PROPERTY_NOTE = compact("""
    The :attr:`{name}` property is a :class:`~{type}`.
""")

DYNAMIC_PROPERTY_NOTE = compact("""
    The :attr:`{name}` property is a dynamically constructed
    subclass of :class:`~{type}`.
""")

REQUIRED_PROPERTY_NOTE = compact("""
    You are required to provide a value for this property by calling the
    constructor of the class that defines the property with a keyword argument
    named `{name}` (unless a custom constructor is defined, in this case please
    refer to the documentation of that constructor).
""")

WRITABLE_PROPERTY_NOTE = compact("""
    You can change the value of this property using normal attribute assignment
    syntax.
""")

CACHED_PROPERTY_NOTE = compact("""
    This property's value is computed once (the first time it is accessed) and
    the result is cached.
""")

RESETTABLE_CACHED_PROPERTY_NOTE = compact("""
    To clear the cached value you can use :keyword:`del` or
    :func:`delattr()`.
""")

RESETTABLE_WRITABLE_PROPERTY_NOTE = compact("""
    To reset it to its default (computed) value you can use :keyword:`del` or
    :func:`delattr()`.
""")


class PropertyManager(object):

    """
    Superclass for classes that use the computed properties from this module.

    Provides support for required properties, setting of properties in the
    constructor and generating a useful textual representation of objects with
    properties.
    """

    def __init__(self, **kw):
        """
        Initialize a :class:`PropertyManager` object.

        :param kw: Any keyword arguments are passed on to :func:`set_properties()`.
        """
        self.set_properties(**kw)
        missing_properties = self.missing_properties
        if missing_properties:
            msg = "missing %s" % pluralize(len(missing_properties), "required argument")
            raise TypeError("%s (%s)" % (msg, concatenate(missing_properties)))

    def set_properties(self, **kw):
        """
        Set instance properties from keyword arguments.

        :param kw: Every keyword argument is used to assign a value to the
                   instance property whose name matches the keyword argument.
        :raises: :exc:`~exceptions.TypeError` when a keyword argument doesn't
                 match a :class:`property` on the given object.
        """
        for name, value in kw.items():
            if self.have_property(name):
                setattr(self, name, value)
            else:
                msg = "got an unexpected keyword argument %r"
                raise TypeError(msg % name)

    @property
    def missing_properties(self):
        """
        The names of required properties that are missing.

        This is a list of strings with the names of required properties that
        either haven't been set or are set to :data:`None`.
        """
        return [n for n in self.required_properties if getattr(self, n, None) is None]

    @property
    def required_properties(self):
        """A list of strings with the names of any required properties."""
        return [n for n in self.find_properties(required=True)]

    def find_properties(self, **options):
        """
        Find an object's properties (of a certain type).

        :param options: Passed on to :func:`have_property()` to enable
                        filtering properties by the operations they support.
        :returns: A list of strings with the names of properties.
        """
        return sorted(n for n in dir(self) if self.have_property(n, **options))

    def have_property(self, name, **options):
        """
        Check if the object has a property (of a certain type).

        :param name: The name of the property (a string).
        :param options: Any keyword arguments give the name of an option
                        (one of :attr:`~custom_property.writable`,
                        :attr:`~custom_property.resettable`,
                        :attr:`~custom_property.cached`,
                        :attr:`~custom_property.required`,
                        :attr:`~custom_property.repr`) and an expected value
                        (:data:`True` or :data:`False`). Filtering on more than
                        one option is supported.
        :returns: :data:`True` if the object has a property with the expected
                  options enabled/disabled, :data:`False` otherwise.
        """
        property_type = getattr(self.__class__, name, None)
        if isinstance(property_type, property):
            if options:
                return all(getattr(property_type, n, None) == v
                           or n == 'repr' and v is True and getattr(property_type, n, None) is not False
                           for n, v in options.items())
            else:
                return True
        else:
            return False

    def clear_cached_properties(self):
        """Clear cached properties so that their values are recomputed."""
        for name in self.find_properties(cached=True, resettable=True):
            delattr(self, name)

    def __repr__(self):
        """
        Render a human friendly string representation of an object with computed properties.

        This method generates a user friendly textual representation for
        objects that use computed properties created using the
        :mod:`property_manager` module. By default it assumes that *all such
        properties* are idempotent and may be called at discretion without
        worrying too much about performance.
        """
        fields = []
        for name in self.find_properties(repr=True):
            value = getattr(self, name, NOTHING)
            if value is not NOTHING:
                fields.append("%s=%r" % (name, value))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(fields))


class custom_property(property):

    """
    Custom :class:`property` subclass that supports additional features.

    The :class:`custom_property` class implements Python's `descriptor
    protocol`_ to provide a decorator that turns methods into computed
    properties with several additional features.

    .. _descriptor protocol: https://docs.python.org/2/howto/descriptor.html

    The additional features are controlled by attributes defined on the
    :class:`custom_property` class. These attributes are intended to be changed
    by the constructor (:func:`__new__()`) and/or classes that inherit from
    :class:`custom_property`:

    .. attribute:: writable

       If this attribute is set to :data:`True` (it defaults to :data:`False`)
       the property supports assignment. The assigned value is stored in the
       :attr:`~object.__dict__` of the object that owns the property.

       :see also: :class:`writable_property`, :class:`mutable_property` and
                  :class:`required_property`.

       A relevant note about how Python looks up attributes: When an attribute
       is looked up and exists in an object's :attr:`~object.__dict__` Python
       ignores any property (descriptor) by the same name and immediately
       returns the value that was found in the object's
       :attr:`~object.__dict__`.

    .. attribute:: resettable

       If this attribute is set to :data:`True` (it defaults to :data:`False`)
       the property can be reset to its default or computed value using
       :keyword:`del` and :func:`delattr()`. This works by removing the
       assigned or cached value from the object's :attr:`~object.__dict__`.

       :see also: :class:`mutable_property` and :class:`cached_property`.

    .. attribute:: cached

       If this attribute is set to :data:`True` (it defaults to :data:`False`)
       the property's value is computed only once and then cached in an
       object's :attr:`~object.__dict__`. The next time you access the
       attribute's value the cached value is automatically returned. By
       combining the :attr:`cached` and :attr:`resettable` options you get a
       cached property whose cached value can be cleared. If the value should
       never be recomputed then don't enable the :attr:`resettable` option.

       :see also: :class:`cached_property` and :class:`lazy_property`.

    .. attribute:: required

       If this attribute is set to :data:`True` (it defaults to :data:`False`)
       the property requires a value to be set during the initialization of the
       object that owns the property. For this to work the class that owns the
       property needs to inherit from :class:`PropertyManager`.

       :see also: :class:`required_property`.

       The constructor of :class:`PropertyManager` will ensure that required
       properties are set to values that aren't :data:`None`. Required
       properties must be set by providing keyword arguments to the constructor
       of the class that inherits from :class:`PropertyManager`. When
       :func:`PropertyManager.__init__()` notices that required properties
       haven't been set it raises a :exc:`~exceptions.TypeError` similar to the
       type error raised by Python when required arguments are missing in a
       function call. Here's an example:

       .. code-block:: python

          from property_manager import PropertyManager, required_property, mutable_property

          class Example(PropertyManager):

              @required_property
              def important(self):
                  "A very important attribute."

              @mutable_property
              def optional(self):
                  "A not so important attribute."
                  return 13

       Let's construct an instance of the class defined above:

       >>> Example()
       Traceback (most recent call last):
         File "property_manager/__init__.py", line 107, in __init__
           raise TypeError("%s (%s)" % (msg, concatenate(missing_properties)))
       TypeError: missing 1 required argument ('important')

       As expected it complains that a required property hasn't been
       initialized. Here's how it's supposed to work:

       >>> Example(important=42)
       Example(important=42, optional=13)

    .. attribute:: repr

       By default :func:`PropertyManager.__repr__()` includes the names and
       values of all properties that aren't :data:`None` in :func:`repr()`
       output. If you want to omit a certain property (e.g. because the value
       contains a secret that shouldn't be exposed or because the value is
       expensive to calculate) you can set :attr:`repr` to :data:`False` (it
       defaults to :data:`True`).

    .. attribute:: dynamic

       :data:`True` when the :class:`custom_property` subclass was dynamically
       constructed by :func:`__new__()`, :data:`False` otherwise. Used by
       :func:`compose_usage_notes()` to decide whether to link to the
       documentation of the subclass or not (because it's impossible to link
       to anonymous classes).
    """

    writable = False
    resettable = False
    required = False
    cached = False
    repr = True
    dynamic = False

    def __new__(cls, *args, **options):
        """
        Constructor for :class:`custom_property` subclasses and instances.

        To construct a subclass:

        :param args: The first positional argument is used as the name of the
                     subclass (defaults to 'customized_property').
        :param options: Each keyword argument gives the name of an option
                        (:attr:`writable`, :attr:`resettable`, :attr:`cached`,
                        :attr:`required`, :attr:`repr`) and the value to use
                        for that option (:data:`True` or :data:`False`).
        :returns: A dynamically constructed subclass of
                  :class:`custom_property` with the given options.

        To construct an instance:

        :param args: The first positional argument is the function that's
                     called to compute the value of the property.
        :returns: A :class:`custom_property` instance corresponding to the
                  class whose constructor was called.

        Here's an example of how the subclass constructor can be used to
        dynamically construct custom properties with specific options:

        .. code-block:: python

           from property_manager import custom_property

           class WritableCachedPropertyDemo(object):

               @custom_property(cached=True, writable=True)
               def customized_test_property(self):
                   return 42

        The example above defines and uses a property whose computed value is
        cached and which supports assignment of new values. The example could
        have been made even simpler:

        .. code-block:: python

           from property_manager import cached_property

           class WritableCachedPropertyDemo(object):

               @cached_property(writable=True)
               def customized_test_property(self):
                   return 42

        Basically you can take any of the custom property classes defined in
        the :mod:`property_manager` module and call the class with keyword
        arguments corresponding to the options you'd like to change.
        """
        if options:
            # Keyword arguments construct subclasses.
            name = args[0] if args else 'customized_property'
            options['dynamic'] = True
            return type(name, (cls,), options)
        else:
            # Positional arguments construct instances.
            return super(custom_property, cls).__new__(cls, *args)

    def __init__(self, func):
        """
        Initialize a :class:`custom_property` object.

        :param func: The function that's called to compute the property's
                     value. The :class:`custom_property` instance inherits the
                     values of :attr:`~object.__doc__`, :attr:`~object.__module__`
                     and :attr:`~object.__name__` from the function.
        :raises: :exc:`~exceptions.ValueError` when the first positional
                 argument is not callable (e.g. a function).

        Automatically calls :func:`inject_usage_notes()` during initialization.
        """
        if not callable(func):
            msg = "Expected to decorate callable, got %r instead!"
            raise ValueError(msg % type(func).__name__)
        else:
            super(custom_property, self).__init__(func)
            self.__doc__ = func.__doc__
            self.__module__ = func.__module__
            self.__name__ = func.__name__
            self.func = func
            self.inject_usage_notes()

    def inject_usage_notes(self):
        """
        Inject the property's semantics into its documentation.

        Calls :func:`compose_usage_notes()` to get a description of the property's
        semantics and appends this to the property's documentation. If the
        property doesn't have documentation it will not be added.
        """
        if self.__doc__ and isinstance(self.__doc__, basestring):
            notes = self.compose_usage_notes()
            if notes:
                self.__doc__ = "\n\n".join([
                    textwrap.dedent(self.__doc__),
                    ".. note:: %s" % " ".join(notes),
                ])

    def compose_usage_notes(self):
        """
        Get a description of the property's semantics to include in its documentation.

        :returns: A list of strings describing the semantics of the
                  :class:`custom_property` in reStructuredText_ format with
                  Sphinx_ directives.

        .. _reStructuredText: https://en.wikipedia.org/wiki/ReStructuredText
        .. _Sphinx: http://sphinx-doc.org/
        """
        template = DYNAMIC_PROPERTY_NOTE if self.dynamic else CUSTOM_PROPERTY_NOTE
        cls = custom_property if self.dynamic else self.__class__
        dotted_path = "%s.%s" % (cls.__module__, cls.__name__)
        notes = [format(template, name=self.__name__, type=dotted_path)]
        if self.required:
            notes.append(format(REQUIRED_PROPERTY_NOTE, name=self.__name__))
        if self.writable:
            notes.append(WRITABLE_PROPERTY_NOTE)
        if self.cached:
            notes.append(CACHED_PROPERTY_NOTE)
        if self.resettable:
            if self.cached:
                notes.append(RESETTABLE_CACHED_PROPERTY_NOTE)
            else:
                notes.append(RESETTABLE_WRITABLE_PROPERTY_NOTE)
        return notes

    def __get__(self, obj, type=None):
        """
        Get the assigned, cached or computed value of the property.

        :param obj: The instance that owns the property.
        :param type: The class that owns the property.
        :returns: The value of the property.
        """
        if obj is None:
            # Called to get the attribute of the class.
            return self
        else:
            # Called to get the attribute of an instance.
            if self.writable or self.cached:
                # Check if a value has been assigned or cached.
                value = obj.__dict__.get(self.__name__, NOTHING)
                if value is not NOTHING:
                    return value
            # Compute the property's value.
            value = self.func(obj)
            if self.cached:
                # Cache the computed value.
                obj.__dict__[self.__name__] = value
            return value

    def __set__(self, obj, value):
        """
        Override the computed value of the property.

        :param obj: The instance that owns the property.
        :param value: The new value for the property.
        :raises: :exc:`~exceptions.AttributeError` if :attr:`writable` is
                 :data:`False`.
        """
        if not self.writable:
            msg = "%r object attribute %r is read-only"
            raise AttributeError(msg % (obj.__class__.__name__, self.__name__))
        obj.__dict__[self.__name__] = value

    def __delete__(self, obj):
        """
        Reset the assigned or cached value of the property.

        :param obj: The instance that owns the property.
        :raises: :exc:`~exceptions.AttributeError` if :attr:`resettable` is
                 :data:`False`.

        Once the property has been deleted the next read will evaluate the
        decorated function to compute the value.
        """
        if not self.resettable:
            msg = "%r object attribute %r is read-only"
            raise AttributeError(msg % (obj.__class__.__name__, self.__name__))
        obj.__dict__.pop(self.__name__, None)


class writable_property(custom_property):

    """
    A computed property that supports assignment.

    This is a variant of :class:`custom_property`
    that has the :attr:`~custom_property.writable`
    option enabled by default.
    """

    writable = True


class required_property(writable_property):

    """
    A property that requires a value to be set.

    This is a variant of :class:`writable_property` that has the
    :attr:`~custom_property.required` option enabled by default. Refer to the
    documentation of the :attr:`~custom_property.required` option for an
    example.
    """

    required = True


class mutable_property(writable_property):

    """
    A computed property that can be assigned and reset.

    This is a variant of :class:`writable_property` that
    has the :attr:`~custom_property.resettable`
    option enabled by default.
    """

    resettable = True


class lazy_property(custom_property):

    """
    A computed property whose value is computed once and cached.

    This is a variant of :class:`custom_property` that
    has the :attr:`~custom_property.cached`
    option enabled by default.
    """

    cached = True


class cached_property(lazy_property):

    """
    A computed property whose value is computed once and cached, but can be reset.

    This is a variant of :class:`lazy_property` that
    has the :attr:`~custom_property.resettable`
    option enabled by default.
    """

    resettable = True
