# Tests of custom properties for Python programming.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: October 4, 2015
# URL: https://property-manager.readthedocs.org

"""Automated tests for the :mod:`property_manager` module."""

# Standard library modules.
import random
import unittest

# External dependencies.
from humanfriendly import format

# Modules included in our package.
from property_manager import (
    cached_property,
    CACHED_PROPERTY_NOTE,
    custom_property,
    CUSTOM_PROPERTY_NOTE,
    lazy_property,
    mutable_property,
    PropertyManager,
    required_property,
    REQUIRED_PROPERTY_NOTE,
    RESETTABLE_CACHED_PROPERTY_NOTE,
    RESETTABLE_WRITABLE_PROPERTY_NOTE,
    writable_property,
    WRITABLE_PROPERTY_NOTE,
)


class PropertyManagerTestCase(unittest.TestCase):

    """Container for the :mod:`property_manager` test suite."""

    def test_builtin_property(self):
        """Test that our assumptions about the behavior of :class:`property` are correct."""
        class NormalPropertyTest(object):
            @property
            def normal_test_property(self):
                return random.random()
        with PropertyInspector(NormalPropertyTest, 'normal_test_property') as p:
            assert p.is_recognizable
            assert p.is_recomputed
            assert p.is_read_only
            assert not p.is_injectable

    def test_custom_property(self):
        """Test that :class:`.custom_property` works just like :class:`property`."""
        class CustomPropertyTest(object):
            @custom_property
            def custom_test_property(self):
                return random.random()
        with PropertyInspector(CustomPropertyTest, 'custom_test_property') as p:
            assert p.is_recognizable
            assert p.is_recomputed
            assert p.is_read_only
            assert not p.is_injectable
            p.check_usage_notes()
        # Test that custom properties expect a function argument and validate their assumption.
        self.assertRaises(ValueError, custom_property, None)

    def test_writable_property(self):
        """Test that :class:`.writable_property` supports assignment."""
        class WritablePropertyTest(object):
            @writable_property
            def writable_test_property(self):
                return random.random()
        with PropertyInspector(WritablePropertyTest, 'writable_test_property') as p:
            assert p.is_recognizable
            assert p.is_recomputed
            assert p.is_writable
            assert not p.is_resettable
            assert p.is_injectable
            p.check_usage_notes()

    def test_required_property(self):
        """Test that :class:`.required_property` performs validation."""
        class RequiredPropertyTest(PropertyManager):
            @required_property
            def required_test_property(self):
                pass
        with PropertyInspector(RequiredPropertyTest, 'required_test_property', required_test_property=42) as p:
            assert p.is_recognizable
            assert p.is_writable
            assert not p.is_resettable
            assert p.is_injectable
            p.check_usage_notes()
        # Test that required properties must be set using the constructor.
        self.assertRaises(TypeError, RequiredPropertyTest)

    def test_mutable_property(self):
        """Test that :class:`mutable_property` supports assignment and deletion."""
        class MutablePropertyTest(object):
            @mutable_property
            def mutable_test_property(self):
                return random.random()
        with PropertyInspector(MutablePropertyTest, 'mutable_test_property') as p:
            assert p.is_recognizable
            assert p.is_recomputed
            assert p.is_writable
            assert p.is_resettable
            assert p.is_injectable
            p.check_usage_notes()

    def test_lazy_property(self):
        """Test that :class:`lazy_property` caches computed values."""
        class LazyPropertyTest(object):
            @lazy_property
            def lazy_test_property(self):
                return random.random()
        with PropertyInspector(LazyPropertyTest, 'lazy_test_property') as p:
            assert p.is_recognizable
            assert p.is_cached
            assert p.is_read_only
            p.check_usage_notes()

    def test_cached_property(self):
        """Test that :class:`.cached_property` caches its result."""
        class CachedPropertyTest(object):
            @cached_property
            def cached_test_property(self):
                return random.random()
        with PropertyInspector(CachedPropertyTest, 'cached_test_property') as p:
            assert p.is_recognizable
            assert p.is_cached
            assert not p.is_writable
            assert p.is_resettable
            p.check_usage_notes()

    def test_property_manager_repr(self):
        """Test :func:`repr()` rendering of :class:`PropertyManager` objects."""
        class RepresentationTest(PropertyManager):
            @required_property
            def important(self):
                pass

            @mutable_property
            def optional(self):
                return 42
        instance = RepresentationTest(important=1)
        assert "important=1" in repr(instance)
        assert "optional=42" in repr(instance)

    def test_property_injection(self):
        """Test that :class:`.PropertyManager` raises an error for unknown properties."""
        class PropertyInjectionTest(PropertyManager):
            @mutable_property
            def injected_test_property(self):
                return 'default'
        assert PropertyInjectionTest().injected_test_property == 'default'
        assert PropertyInjectionTest(injected_test_property='injected').injected_test_property == 'injected'
        self.assertRaises(TypeError, PropertyInjectionTest, random_keyword_argument=True)

    def test_property_customization(self):
        """Test that :func:`.custom_property.__new__()` dynamically constructs subclasses."""
        class CustomizedPropertyTest(object):
            @custom_property(cached=True, writable=True)
            def customized_test_property(self):
                pass
        with PropertyInspector(CustomizedPropertyTest, 'customized_test_property') as p:
            assert p.is_recognizable
            assert p.is_cached
            assert p.is_writable

    def test_cache_invalidation(self):
        """Test that :func:`.PropertyManager.clear_cached_properties()` correctly clears cached property values."""
        class CacheInvalidationTest(PropertyManager):

            def __init__(self, counter):
                self.counter = counter

            @lazy_property
            def lazy(self):
                return self.counter * 2

            @cached_property
            def cached(self):
                return self.counter * 2

        instance = CacheInvalidationTest(42)
        # Test that the lazy property was calculated based on the input.
        assert instance.lazy == (42 * 2)
        # Test that the cached property was calculated based on the input.
        assert instance.cached == (42 * 2)
        # Invalidate the values of cached properties.
        instance.counter *= 2
        instance.clear_cached_properties()
        assert instance.lazy == (42 * 2)
        assert instance.cached == (42 * 2 * 2)


class PropertyInspector(object):

    """Introspecting properties with properties (turtles all the way down)."""

    def __init__(self, owner, name, *args, **kw):
        """
        Initialize a :class:`PropertyInspector` object.

        :param owner: The class that owns the property.
        :param name: The name of the property (a string).
        :param args: Any positional arguments needed to initialize an instance
                     of the owner class.
        :param kw: Any keyword arguments needed to initialize an instance of
                   the owner class.
        """
        self.owner_object = owner(*args, **kw)
        self.owner_type = owner
        self.property_name = name
        self.property_object = getattr(owner, name)
        self.property_type = self.property_object.__class__

    def __enter__(self):
        """Enable the syntax of context managers."""
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        """Enable the syntax of context managers."""
        pass

    @property
    def value(self):
        """Get the value of the property from the owner's instance."""
        return getattr(self.owner_object, self.property_name)

    @property
    def is_recognizable(self):
        """
        :data:`True` if the property can be easily recognized, :data:`False` otherwise.

        This function confirms that custom properties subclass Python's built
        in :class:`property` class so that introspection of class members using
        :func:`isinstance()` correctly recognizes properties as such, even for
        code which is otherwise unaware of the custom properties defined by the
        :mod:`property_manager` module.
        """
        return isinstance(self.property_object, property)

    @property
    def is_recomputed(self):
        """:data:`True` if the property is recomputed each time, :data:`False` otherwise."""
        return not self.is_cached

    @property
    def is_cached(self):
        """:data:`True` if the property is cached (not recomputed), :data:`False` otherwise."""
        class CachedPropertyTest(object):
            @self.property_type
            def value(self):
                return random.random()
        obj = CachedPropertyTest()
        return (obj.value == obj.value)

    @property
    def is_read_only(self):
        """:data:`True` if the property is read only, :data:`False` otherwise."""
        return not self.is_writable and not self.is_resettable

    @property
    def is_writable(self):
        """:data:`True` if the property supports assignment, :data:`False` otherwise."""
        unique_value = object()
        try:
            setattr(self.owner_object, self.property_name, unique_value)
            return getattr(self.owner_object, self.property_name) is unique_value
        except AttributeError:
            return False

    @property
    def is_resettable(self):
        """:data:`True` if the property can be reset to its computed value, :data:`False` otherwise."""
        try:
            delattr(self.owner_object, self.property_name)
            return True
        except AttributeError:
            return False

    @property
    def is_injectable(self):
        """:data:`True` if the property can be set via the owner's constructor, :data:`False` otherwise."""
        initial_value = object()
        injected_value = object()
        try:
            class PropertyOwner(PropertyManager):
                @self.property_type
                def test_property(self):
                    return initial_value
            clean_instance = PropertyOwner()
            injected_instance = PropertyOwner(test_property=injected_value)
            return clean_instance.test_property is initial_value and injected_instance.test_property is injected_value
        except AttributeError:
            return False

    def check_usage_notes(self):
        """"Check whether the correct notes are embedded in the documentation."""
        class DocumentationTest(object):
            @self.property_type
            def documented_property(self):
                """Documentation written by the author."""
                return random.random()
        documentation = DocumentationTest.documented_property.__doc__
        # Test that the sentence added for custom properties is always present.
        custom_property_note = format(CUSTOM_PROPERTY_NOTE,
                                      name='documented_property',
                                      type="%s.%s" % (self.property_type.__module__,
                                                      self.property_type.__name__))
        assert custom_property_note in documentation
        # Test that the sentence added for writable properties is present when applicable.
        assert self.property_type.writable == (WRITABLE_PROPERTY_NOTE in documentation)
        # Test that the sentence added for cached properties is present when applicable.
        assert self.property_type.cached == (CACHED_PROPERTY_NOTE in documentation)
        # Test that the sentence added for resettable properties is present when applicable.
        if self.is_resettable:
            assert self.is_cached == (RESETTABLE_CACHED_PROPERTY_NOTE in documentation)
            assert self.is_writable == (RESETTABLE_WRITABLE_PROPERTY_NOTE in documentation)
        else:
            assert RESETTABLE_CACHED_PROPERTY_NOTE not in documentation
            assert RESETTABLE_WRITABLE_PROPERTY_NOTE not in documentation
        # Test that the sentence added for required properties is present when applicable.
        required_property_note = format(REQUIRED_PROPERTY_NOTE, name='documented_property')
        assert self.property_type.required == (required_property_note in documentation)
