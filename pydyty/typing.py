import types


class Typing(object):
    """ This class serves as staticmethod grouping related to subtyping. """

    @staticmethod
    def _is_top_subtype(l_t, r_t):
        return isinstance(r_t, l_t.__class__)

    @staticmethod
    def _is_bottom_subtype(l_t, r_t):
        return True

    @staticmethod
    def _is_nominal_subtype_of_nominal(l_t, r_t):
        if l_t == r_t:
            return True
        # TODO: check subtype relationship here.
        return False

    @staticmethod
    def _is_nominal_subtype(l_t, r_t):
        if isinstance(r_t, types.NominalType):
            result = Typing._is_nominal_subtype_of_nominal(l_t, r_t)
        else:
            raise Exception('Not yet implemented')
        return result

    @staticmethod
    def _is_method_subtype_of_method(l_t, r_t):
        result = True
        for idx, r_t_arg_type in enumerate(r_t.arg_types):
            if idx >= len(l_t.arg_types):
                result = False
                break
            if not Typing.is_subtype(r_t_arg_type, l_t.arg_types[idx]):
                result = False
                break
        if result:
            for name, r_t_kwarg_type in r_t.kwarg_types.items():
                l_t_kwarg_type = l_t.kwarg_types.get(name, None)
                if l_t_kwarg_type is None:
                    result = False
                    break
                if not Typing.is_subtype(r_t_kwarg_type, l_t_kwarg_type):
                    result = False
                    break
        if result:
            result = Typing.is_subtype(l_t.ret_type, r_t.ret_type)
        return result

    @staticmethod
    def _is_method_subtype(l_t, r_t):
        """ Assumes l_t IS a method type. """
        if isinstance(r_t, types.MethodType):
            # life is easier
            result = Typing._is_method_subtype_of_method(l_t, r_t)
        else:
            result = False
        return result

    @staticmethod
    def _is_object_subtype_of_object(l_t, r_t):
        result = True
        if len(l_t.methods) < len(r_t.methods):
            result = False
        else:
            for meth_name, meth_type in l_t.methods.iteritems():
                if meth_name not in r_t.methods:
                    result = False
                    break
                r_t_meth_type = r_t.methods[meth_name]
                if not Typing._is_method_subtype(meth_type, r_t_meth_type):
                    result = False
                    break
        return result

    @staticmethod
    def _is_object_subtype_of_nominal(l_t, r_t):
        pass

    @staticmethod
    def _is_object_subtype(l_t, r_t):

        if isinstance(r_t, types.ObjectType):
            result = Typing._is_object_subtype_of_object(l_t, r_t)
        elif isinstance(r_t, types.NominalType):
            raise Exception("Not yet implemented")
        else:
            result = False
        return result

    @staticmethod
    def is_subtype(l_t, r_t):
        if isinstance(l_t, types.TopType):
            return Typing._is_top_subtype(l_t, r_t)
        elif isinstance(l_t, types.BottomType):
            return Typing._is_bottom_subtype(l_t, r_t)
        elif isinstance(l_t, types.NominalType):
            return Typing._is_nominal_subtype(l_t, r_t)
        elif isinstance(l_t, types.MethodType):
            return Typing._is_method_subtype(l_t, r_t)
        elif isinstance(l_t, types.ObjectType):
            return Typing._is_object_subtype(l_t, r_t)
