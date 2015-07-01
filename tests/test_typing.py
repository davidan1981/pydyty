from base_test import BaseTestCase
from pydyty import types
from pydyty.typing import Typing


class TestTyping(BaseTestCase):

    def setUp(self):
        super(TestTyping, self).setUp()

    def tearDown(self):
        super(TestTyping, self).tearDown()

    def test_top_type(self):
        l_t = types.TopType()
        r_t = types.TopType()
        self.assertTrue(Typing.is_subtype(l_t, r_t))
        r_t = types.BottomType()
        self.assertFalse(Typing.is_subtype(l_t, r_t))

    def test_bottom_type(self):
        l_t = types.BottomType()
        r_t = types.TopType()
        self.assertTrue(Typing.is_subtype(l_t, r_t))
        r_t = types.BottomType()
        self.assertTrue(Typing.is_subtype(l_t, r_t))

    def test_nominal_type(self):
        l_t = types.NominalType('A')
        r_t = types.NominalType('A')
        self.assertTrue(Typing.is_subtype(l_t, r_t))

    def test_method_and_method_no_args_nominal_ret(self):
        l_rt = types.NominalType('A')
        l_mt = types.MethodType([], {}, l_rt)
        r_rt = types.NominalType('A')
        r_mt = types.MethodType([], {}, r_rt)
        self.assertTrue(Typing.is_subtype(l_mt, r_mt))

    def test_method_and_method_no_args_nominal_ret_not_subtype(self):
        l_rt = types.NominalType('A')
        l_mt = types.MethodType([], {}, l_rt)
        r_rt = types.NominalType('B')
        r_mt = types.MethodType([], {}, r_rt)
        self.assertFalse(Typing.is_subtype(l_mt, r_mt))
