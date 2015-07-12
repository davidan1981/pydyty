import traceback
import types
from pydyty.loc import Location


class ObjectWrapper(object):
    """ Wraps an object and gathers type information about the object within
    a context. For our purose, this means a method call. At each method
    call, each argument will be wrapped. Then, any calls to that object is
    "sniffed" by this wrapper, determining the type of the object within the
    method."""

    def __init__(self, obj):
        """ Wraps around the object with a new ObjectWrapper instance."""

        self.__pydyty__ = True

        if hasattr(obj, "__pydyty__"):
            self.__pydyty_obj__ = obj.__pydyty_obj__
        else:
            self.__pydyty_obj__ = obj

        if hasattr(obj, "__dict__"):
            self.__pydyty_type__ = types.ObjectType()
        else:
            self.__pydyty_type__ = types.NominalType(obj, is_object=True)

    def __getattribute__(self, name):
        """ This takes a complete control over attribute access. Any non
        __pydyty_* attributes will result in an AttributeError which
        triggers __getattr__ method. """

        attr = object.__getattribute__(self, name)
        return attr

    def __setattr__(self, name, value):
        """ Any attribute setter call is routed to here."""

        if not name.startswith('__pydyty'):
            object.__setattr__(self.__pydyty_obj__, name, value)
            self.__pydyty_type__.add_attr(name, types.NominalType(value, is_object=True))  # noqa
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        """ Any non-__pydyty_* attributes will be routed to here. There are
        methods and fields, which are distinguished by checking '__call__'
        attribute on the attribute being routed for."""

        def __method_missing__(*args, **kwargs):
            """ This nested function is invoked when the attribute (method)
            is invoked. It records the types of the arguments, runs the
            original method, records the return type, and returns the actual
            result of the original method call."""

            # Try to get the caller information
            loc = Location.create(traceback.extract_stack()[-2])

            # Get types of the arguments
            arg_types = []
            for arg in args:
                if hasattr(arg, "__pydyty__"):
                    arg_types.append(arg.__pydyty_type__)
                else:
                    arg_types.append(types.NominalType(arg, is_object=True,
                                     loc=loc))

            # Get types of the dictionary arguments
            kwarg_types = {}
            for kwarg_name, kwarg_val in kwargs.iteritems():
                if hasattr(kwarg_val, '__pydyty__'):
                    kwarg_type = kwarg_val.__pydyty_type__
                else:
                    kwarg_type = types.NominalType(kwarg_val, is_object=True,
                                                   loc=loc)
                kwarg_types[kwarg_name] = kwarg_type

            # Lastly, return type. Run the original method first.
            ret_val = attr(*args, **kwargs)
            ret_type = types.NominalType(ret_val, is_object=True, loc=loc)
            method_type = types.MethodType(arg_types, kwarg_types, ret_type,
                                           loc=loc)

            self.__pydyty_type__.add_attr(name, method_type)
            return ret_val

        # Two possibilities: method and field
        # If it's a method, return __method_missing__ which will be executed
        # at the method invocation. If it's a field, get the type and return
        # the value.

        attr = getattr(self.__pydyty_obj__, name)
        if hasattr(attr, '__call__'):
            return __method_missing__

        # Try to get the caller information
        loc = Location.create(traceback.extract_stack()[-1])

        self.__pydyty_type__.add_attr(
            name, types.NominalType(attr, is_object=True, loc=loc))

        return attr
