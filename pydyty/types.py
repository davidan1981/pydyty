# import logging
from typing import Typing
from errors import AbstractClassError
from errors import NominalTypeInitError


class PydytyType(object):
    """ Abstract type to represent a type. """

    def __init__(self, loc=None, **kwargs):
        self.loc = loc

    def __str__(self):
        raise AbstractClassError()

    def __eq__(self, other):
        raise AbstractClassError()

    def __ne__(self, other):
        return not self.__eq__(other)

    def add_loc(self, loc):
        if self.loc is not None:
            self.loc.add_loc(loc)
        else:
            self.loc = loc


class TopType(PydytyType):
    """ Represents the top type of all. Should not be used in real life.
    Only used to represent untyped/uninferred methods/properties."""

    def __str__(self):
        return '<<Top>>'

    def __eq__(self, other):
        return isinstance(other, TopType)


class BottomType(PydytyType):
    """ Represents the bottom type. Should not be used in real life. Only
    used to represent untyped/uninferred methods/properties."""

    def __str__(self):
        return '<<Bottom>>'

    def __eq__(self, other):
        return isinstance(other, BottomType)


class CompositeType(PydytyType):
    """ Abstract type that consists of one or more types."""

    def __init__(self, types, **kwargs):
        super(CompositeType, self).__init__(**kwargs)
        self.types = types

    def add_type(self, _type):
        """ Adds another type to the list of possible types. """
        self.types.append(_type)
        self.add_loc(_type.loc)
        return self

    def __str__(self):
        raise AbstractClassError()

    def __eq__(self, other):
        result = isinstance(other, self.__class__)
        if result:
            if len(self.types) != len(other.types):
                result = False
        if result:
            for i, t in enumerate(self.types):
                if t != other.types[i]:
                    result = False
                    break
        return result


class UnionType(CompositeType):
    """ Represents an union type. This can be any of the types expressed in
    the union type. To avoid complicated typing, we will not be using this
    with method types."""

    def __str__(self):
        return ' or '.join(['(%s)' % str(t) for t in self.types])


class IntersectionType(CompositeType):
    """ Represents an intersection type. This means ALL of the types
    expressed in this type must be true. This is a complicated type. So we
    apply this only to methods."""

    def __str__(self):
        s = ' and '.join(['(%s)' % str(t) for t in self.types])
        return s


class MethodType(PydytyType):
    """ Represents a method (function) type. In type theory, there is
    actually no difference. One is bound and the other is unbound. Since
    Python keeps track of this by having 'self' or 'cls' in the signature,
    that's how we are going to do as well.

    """

    def __init__(self, arg_types=[], kwarg_types={}, ret_type=None, **kwargs):
        super(MethodType, self).__init__(**kwargs)
        self.arg_types = arg_types
        self.kwarg_types = kwarg_types
        self.ret_type = ret_type

    @classmethod
    def create_empty(self, num_of_args, kwarg_keys, **kwargs):
        """ Creates an empty method type using top types for args and kwargs
        and a bottom type for the return type. Used as an initial type for
        inferring methods in a class."""
        arg_types = [TopType(**kwargs) for i in range(0, num_of_args)]
        kwargs_types = {}
        for key in kwarg_keys:
            kwargs_types[key] = TopType(**kwargs)
        ret_type = BottomType(**kwargs)
        return MethodType(arg_types, kwargs_types, ret_type, **kwargs)

    def __str__(self):
        args = [str(arg_type) for arg_type in self.arg_types]
        if args:
            args = ', '.join(args)
        sorted_keys = sorted(self.kwarg_types)
        kwargs = ['%s:%s' % (k, self.kwarg_types[k]) for k in sorted_keys]
        if kwargs:
            kwargs = ', '.join(kwargs)
        if args and kwargs:
            all_args = '%s, %s' % (args, kwargs)
        elif args:
            all_args = args
        elif kwargs:
            all_args = kwargs
        else:
            all_args = ''
        return ('(%s) -> %s' % (all_args, self.ret_type))

    def __eq__(self, other):
        result = isinstance(other, self.__class__)
        if len(self.arg_types) != len(other.arg_types):
            result = False
        if result:
            if len(self.kwarg_types) != len(other.kwarg_types):
                result = False
        if result:
            for i, t in enumerate(self.arg_types):
                if t != other.arg_types[i]:
                    result = False
                    break
        if result:
            sorted_keys = sorted(self.kwarg_types)
            for k in sorted_keys:
                if self.kwarg_types[k] != other.kwarg_types.get(k):
                    result = False
                    break
        return result


class NominalType(PydytyType):
    """ Represents a nominal type. """

    def __init__(self, name_or_obj, is_object=False, **kwargs):
        """ For convenience, we allow either name of the nominal type or an
        object from which you'd like to retrive type information."""
        super(NominalType, self).__init__(**kwargs)
        if is_object:
            if hasattr(name_or_obj, '__class__'):
                self.name = name_or_obj.__class__.__name__
            else:
                self.name = type(name_or_obj).__name__
        elif not isinstance(name_or_obj, basestring):
            raise NominalTypeInitError()
        else:
            self.name = name_or_obj

    def __str__(self):
        return self.name

    def __eq__(self, other):
        result = isinstance(other, self.__class__)
        return result and (self.name == other.name)


class ObjectType(PydytyType):
    """ Represents a structural type. It only represents a single layer
    without a meta layer. In other words, class level type information is
    not part of an object type. Use ClassType. Or use InferredNominalType to
    do both at the same time."""

    def __init__(self, attrs=None, **kwargs):
        super(ObjectType, self).__init__(**kwargs)
        self.attrs = attrs or {}  # NOTE: Python bug??

    def add_attr(self, name, attr_type):
        """ Adds a method to the object type. If there exists an entry
        with the same name, then we do subtyping comparisons to see if we
        can consolidate. If not, we create an intersection type."""
        if name in self.attrs:
            exist_attr_type = self.attrs[name]
            if isinstance(exist_attr_type, IntersectionType):
                exist_attr_type.add_type(attr_type)
            elif Typing.is_subtype(attr_type, exist_attr_type):
                self.attrs[name] = attr_type
            elif Typing.is_subtype(exist_attr_type, attr_type):
                pass
            else:
                attr_type = IntersectionType([exist_attr_type, attr_type])
                self.attrs[name] = attr_type
        else:
            self.attrs[name] = attr_type

    def add_empty_method(self, name, num_of_args, kwarg_keys):
        """ Adds an empty method type to the list. This WILL overwrite the
        existing type for the method if there exists one already."""
        attr_type = MethodType.create_empty(num_of_args, kwarg_keys)
        self.attrs[name] = attr_type

    def __str__(self):
        types = sorted(self.attrs)
        tlist = ['%s: %s' % (n, self.attrs[n]) for n in types]
        return '[%s]' % ', '.join(tlist) if tlist else '[]'

    def __eq__(self, other):
        result = isinstance(other, self.__class__)
        if result:
            if len(self.attrs) != len(other.attrs):
                result = False
        if result:
            for n, t in self.attrs.iteritems():
                other_method = other.attrs.get(n, None)
                if (other_method is None) or t != other.attrs.get(n, None):
                    result = False
                    break
        return result


class FusionType(NominalType, ObjectType):
    """ Similar to ObjectType except it has a name. For instance A[foo, bar]
    can be understood as an object with foo and bar methods like A."""

    def __init__(self, name_or_obj, attrs={},
                 is_object=False, **kwargs):
        NominalType.__init__(self, name_or_obj, is_object)
        ObjectType.__init__(self, attrs=attrs, **kwargs)

    def __str__(self):
        types = sorted(self.attrs)
        tlist = ['%s: %s' % (n, self.attrs[n]) for n in types]
        return '%s[%s]' % (self.name, ', '.join(tlist))

    def __eq__(self, other):
        result = isinstance(other, self.__class__)
        if result:
            result = self.name == other.name
        if result:
            if len(self.attrs) != len(other.attrs):
                result = False
        if result:
            for n, t in self.attrs.iteritems():
                if t != other.attrs.get(n, None):
                    result = False
                    break
        return result
