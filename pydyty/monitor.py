import logging
from . import types
from .object_wrapper import ObjectWrapper


def _invoke(recv, cls_type, func_name, func, *args, **kwargs):
    new_args = []
    new_kwargs = {}

    logging.info("{} is being invoked...".format(func_name))

    for arg in args:
        obj = arg.__pydyty__ if hasattr(arg, '__pydyty__') else arg
        new_args.append(ObjectWrapper(obj))

    for k, v in kwargs.iteritems():
        obj = v.__pydyty__ if hasattr(v, '__pydyty__') else v
        new_kwargs[k] = obj

    result = func(recv, *new_args, **new_kwargs)

    # TODO: gather type information and store in cls

    arg_types = [arg.__pydyty_type__ for arg in new_args]
    kwarg_types = {}
    for k, v in new_kwargs.iteritems():
        kwarg_types[k] = v.__pydyty_type__

    ret_type = types.NominalType(result, is_object=True)

    new_method_type = types.MethodType(arg_types, kwarg_types, ret_type)
    cls_type.add_attr(func_name, new_method_type)

    # The return value might be an ObjectWrapper object (e.g., a formal
    # argument was returned). In that case, strip it.
    if hasattr(result, "__pydyty__"):
        result = result.__pydyty_obj__

    return result


def _proxy(cls_type, func_name, func):
    return (lambda self, *args, **kwargs:
            _invoke(self, cls_type, func_name, func, *args, **kwargs))


class Monitor(type):

    def __new__(cls, name, bases, attrs):

        cls_type = types.ObjectType()  # TODO: probably ClassType()
        setattr(cls, '__pydyty_type__', cls_type)
        new_attrs = {}

        for k, v in attrs.iteritems():
            if hasattr(v, '__call__'):
                logging.info("{} method is being monitored...".format(k))
                new_attrs[k] = _proxy(cls_type, k, v)
            else:
                new_attrs[k] = v

        return super(Monitor, cls).__new__(cls, name, bases, new_attrs)


class Monitored(object):

    __metaclass__ = Monitor
