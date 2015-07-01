from base_test import BaseTestCase
from pydyty import types


class TypeTestCase(BaseTestCase):

    def test_top_type(self):
        self.assertEqual('<<Top>>', str(types.TopType()))

    def test_bottom_type(self):
        self.assertEqual('<<Bottom>>', str(types.BottomType()))

    def test_abstract_types(self):
        t = types.PydytyType()
        with self.assertRaises(Exception):
            str(t)
        with self.assertRaises(Exception):
            t == 1
        t = types.CompositeType([t])
        with self.assertRaises(Exception):
            str(t)

    def test_nominal_type(self):
        t = types.NominalType('A')
        self.assertEqual('A', t.name)
        with self.assertRaises(Exception):
            types.NominalType(1)

    def test_nominal_type_object(self):
        t = types.NominalType(None, is_object=True)
        self.assertEqual('NoneType', t.name)
        t = types.NominalType(1, is_object=True)
        self.assertEqual('int', t.name)

        class ClassA():
            pass

        t = types.NominalType(ClassA, is_object=True)
        self.assertEqual('classobj', t.name)

    def test_union_type_two(self):
        t1 = types.NominalType('A')
        t2 = types.NominalType('B')
        t3 = types.UnionType([t1, t2])
        self.assertEqual('(A) or (B)', str(t3))

    def test_union_type_three(self):
        t1 = types.NominalType('A')
        t2 = types.NominalType('B')
        t3 = types.NominalType('C')
        t4 = types.UnionType([t1, t2, t3])
        self.assertEqual('(A) or (B) or (C)', str(t4))
        t1 = types.NominalType('A')
        t2 = types.NominalType('B')
        t4 = types.UnionType([t1, t2])
        t3 = types.NominalType('C')
        t4.add_type(t3)
        self.assertEqual('(A) or (B) or (C)', str(t4))

    def test_method_type_no_arg(self):
        r_t = types.NominalType('A')
        m_t = types.MethodType([], {}, r_t)
        self.assertEqual('() -> A', str(m_t))
        m_t = types.MethodType.create_empty(1, ['a', 'b'])
        self.assertEqual('(<<Top>>, a:<<Top>>, b:<<Top>>) -> <<Bottom>>',
                         str(m_t))

    def test_method_type_one_arg(self):
        a1_t = types.NominalType('A')
        r_t = types.NominalType('B')
        m_t = types.MethodType([a1_t], {}, r_t)
        self.assertEqual('(A) -> B', str(m_t))

    def test_method_type_two_args(self):
        a1_t = types.NominalType('A')
        a2_t = types.NominalType('B')
        r_t = types.NominalType('C')
        m_t = types.MethodType([a1_t, a2_t], {}, r_t)
        self.assertEqual('(A, B) -> C', str(m_t))

    def test_method_type_two_args_one_kwarg(self):
        a1_t = types.NominalType('A')
        a2_t = types.NominalType('B')
        k1_t = types.NominalType('C')
        r_t = types.NominalType('D')
        m_t = types.MethodType([a1_t, a2_t], {'k1': k1_t}, r_t)
        self.assertEqual('(A, B, k1:C) -> D', str(m_t))

    def test_method_type_two_args_two_kwargs(self):
        a1_t = types.NominalType('A')
        a2_t = types.NominalType('B')
        k1_t = types.NominalType('C')
        k2_t = types.NominalType('D')
        r_t = types.NominalType('E')
        m_t = types.MethodType([a1_t, a2_t], {'k1': k1_t, 'k2': k2_t}, r_t)
        self.assertEqual('(A, B, k1:C, k2:D) -> E', str(m_t))

    def test_method_intersection_types(self):
        a1_t = types.NominalType('A')
        a2_t = types.NominalType('B')
        r_t = types.NominalType('C')
        m1_t = types.MethodType([a1_t, a2_t], {}, r_t)
        a1_t = types.NominalType('D')
        a2_t = types.NominalType('E')
        r_t = types.NominalType('F')
        m2_t = types.MethodType([a1_t, a2_t], {}, r_t)
        i_t = types.IntersectionType([m1_t, m2_t])
        self.assertEqual('((A, B) -> C) and ((D, E) -> F)', str(i_t))

    def test_object_type_no_method(self):
        o_t = types.ObjectType()
        self.assertEqual('[]', str(o_t))

    def test_object_type_one_method(self):
        a1_t = types.NominalType('A')
        r_t = types.NominalType('B')
        m_t = types.MethodType([a1_t], {}, r_t)
        o_t = types.ObjectType({'m': m_t})
        self.assertEqual('[m: (A) -> B]', str(o_t))

    def test_object_type_two_methods(self):
        a1_t = types.NominalType('A')
        r_t = types.NominalType('B')
        m1_t = types.MethodType([a1_t], {}, r_t)
        a1_t = types.NominalType('C')
        r_t = types.NominalType('D')
        m2_t = types.MethodType([a1_t], {}, r_t)
        o_t = types.ObjectType({'m1': m1_t, 'm2': m2_t})
        self.assertEqual('[m1: (A) -> B, m2: (C) -> D]', str(o_t))

    def test_object_type_two_methods_by_adding(self):
        a1_t = types.NominalType('A')
        r_t = types.NominalType('B')
        m1_t = types.MethodType([a1_t], {}, r_t)
        o_t = types.ObjectType({'m1': m1_t})
        a1_t = types.NominalType('C')
        r_t = types.NominalType('D')
        m2_t = types.MethodType([a1_t], {}, r_t)
        o_t.add_attr('m2', m2_t)
        self.assertEqual('[m1: (A) -> B, m2: (C) -> D]', str(o_t))

    def test_object_type_two_same_methods(self):
        a1_t = types.NominalType('A')
        r_t = types.NominalType('B')
        m1_t = types.MethodType([a1_t], {}, r_t)
        o_t = types.ObjectType({'m1': m1_t})
        a1_t = types.NominalType('C')
        r_t = types.NominalType('D')
        m2_t = types.MethodType([a1_t], {}, r_t)
        o_t.add_attr('m1', m2_t)
        self.assertEqual('[m1: ((A) -> B) and ((C) -> D)]', str(o_t))

    def test_object_type_three_same_methods(self):
        a1_t = types.NominalType('A')
        r_t = types.NominalType('B')
        m1_t = types.MethodType([a1_t], {}, r_t)
        o_t = types.ObjectType({'m1': m1_t})
        a1_t = types.NominalType('C')
        r_t = types.NominalType('D')
        m2_t = types.MethodType([a1_t], {}, r_t)
        o_t.add_attr('m1', m2_t)
        a1_t = types.NominalType('E')
        r_t = types.NominalType('F')
        m3_t = types.MethodType([a1_t], {}, r_t)
        o_t.add_attr('m1', m3_t)
        self.assertEqual('[m1: ((A) -> B) and ((C) -> D) and ((E) -> F)]', str(o_t))
        
    def test_fusion_type_one_method(self):
        a1_t = types.NominalType('A')
        r_t = types.NominalType('B')
        m_t = types.MethodType([a1_t], {}, r_t)
        f_t = types.FusionType('Foo', {'m': m_t})
        self.assertEqual('Foo[m: (A) -> B]', str(f_t))

    def test_fusion_type_two_methods(self):
        a1_t = types.NominalType('A')
        r_t = types.NominalType('B')
        m1_t = types.MethodType([a1_t], {}, r_t)
        a1_t = types.NominalType('C')
        r_t = types.NominalType('D')
        m2_t = types.MethodType([a1_t], {}, r_t)
        f_t = types.FusionType('Foo', {'m1': m1_t, 'm2': m2_t})
        self.assertEqual('Foo[m1: (A) -> B, m2: (C) -> D]', str(f_t))

    def test_fusion_type_two_methods_by_adding(self):
        f_t = types.FusionType('Foo')
        a1_t = types.NominalType('A')
        r_t = types.NominalType('B')
        m1_t = types.MethodType([a1_t], {}, r_t)
        f_t.add_attr('m1', m1_t)
        a1_t = types.NominalType('C')
        r_t = types.NominalType('D')
        m2_t = types.MethodType([a1_t], {}, r_t)
        f_t.add_attr('m2', m2_t)
        self.assertEqual('Foo[m1: (A) -> B, m2: (C) -> D]', str(f_t))


class TypeEqualityTestCase(BaseTestCase):

    def test_top_type(self):
        t1 = types.TopType()
        t2 = types.TopType()
        self.assertEqual(t1, t2)
        t3 = types.BottomType()
        self.assertNotEqual(t1, t3)

    def test_bottom_type(self):
        t1 = types.BottomType()
        t2 = types.BottomType()
        self.assertEqual(t1, t2)
        t3 = types.TopType()
        self.assertNotEqual(t1, t3)

    def test_nominal_type(self):
        t1 = types.NominalType('A')
        t2 = types.NominalType('A')
        self.assertEqual(t1, t2)
        t3 = types.NominalType('B')
        self.assertNotEqual(t1, t3)
        t4 = types.TopType()
        self.assertNotEqual(t1, t4)

    def test_empty_union_type(self):
        t1 = types.UnionType([])
        t2 = types.UnionType([])
        self.assertEqual(t1, t2)
        t3 = types.NominalType('A')
        t4 = types.UnionType([t3])
        self.assertNotEqual(t2, t4)

    def test_union_type(self):
        t1 = types.NominalType('A')
        t2 = types.NominalType('B')
        t3 = types.UnionType([t1, t2])
        t4 = types.NominalType('A')
        t5 = types.NominalType('B')
        t6 = types.UnionType([t4, t5])
        self.assertEqual(t3, t6)
        self.assertNotEqual(t3, t4)
        t7 = types.UnionType([t4, t5, t4])
        self.assertNotEqual(t6, t7)
        t8 = types.NominalType('C')
        t9 = types.UnionType([t4, t8])
        self.assertNotEqual(t6, t9)

    def test_empty_method_type(self):
        l_r_t = types.BottomType()
        l_m_t = types.MethodType([], {}, l_r_t)
        r_r_t = types.BottomType()
        r_m_t = types.MethodType([], {}, r_r_t)
        self.assertEqual(l_m_t, r_m_t)

    def test_method_type(self):
        l_a1_t = types.NominalType('A')
        l_a2_t = types.NominalType('B')
        l_k1_t = types.NominalType('C')
        l_k2_t = types.NominalType('D')
        l_r_t = types.NominalType('E')
        l_m_t = types.MethodType([l_a1_t, l_a2_t],
                                 {'c': l_k1_t, 'd': l_k2_t},
                                 l_r_t)
        r_a1_t = types.NominalType('A')
        r_a2_t = types.NominalType('B')
        r_k1_t = types.NominalType('C')
        r_k2_t = types.NominalType('D')
        r_r_t = types.NominalType('E')
        r_m_t = types.MethodType([r_a1_t, r_a2_t],
                                 {'c': r_k1_t, 'd': r_k2_t},
                                 r_r_t)
        self.assertEqual(l_m_t, r_m_t)
        r_a1_t = types.NominalType('A')
        r_a2_t = types.NominalType('B')
        r_k1_t = types.NominalType('C')
        r_k2_t = types.NominalType('E')
        r_r_t = types.NominalType('E')
        r_m_t = types.MethodType([r_a1_t, r_a2_t],
                                 {'c': r_k1_t, 'd': r_k2_t},
                                 r_r_t)
        self.assertNotEqual(l_m_t, r_m_t)
        r_a1_t = types.NominalType('A')
        r_k1_t = types.NominalType('C')
        r_k2_t = types.NominalType('D')
        r_r_t = types.NominalType('E')
        r_m_t = types.MethodType([r_a1_t],
                                 {'c': r_k1_t, 'd': r_k2_t},
                                 r_r_t)
        self.assertNotEqual(l_m_t, r_m_t)
        r_a1_t = types.NominalType('A')
        r_a2_t = types.NominalType('B')
        r_k1_t = types.NominalType('C')
        r_r_t = types.NominalType('E')
        r_m_t = types.MethodType([r_a1_t, r_a2_t],
                                 {'c': r_k1_t},
                                 r_r_t)
        self.assertNotEqual(l_m_t, r_m_t)
        r_a1_t = types.NominalType('A')
        r_a2_t = types.NominalType('E')
        r_k1_t = types.NominalType('C')
        r_k2_t = types.NominalType('D')
        r_r_t = types.NominalType('E')
        r_m_t = types.MethodType([r_a1_t, r_a2_t],
                                 {'c': r_k1_t, 'd': r_k2_t},
                                 r_r_t)
        self.assertNotEqual(l_m_t, r_m_t)

    def test_empty_object_type(self):
        o1_t = types.ObjectType()
        o2_t = types.ObjectType()
        self.assertEqual(o1_t, o2_t)
        r_r_t = types.NominalType('A')
        r_m_t = types.MethodType([], {}, r_r_t)
        o2_t = types.ObjectType({'m': r_m_t})
        self.assertNotEqual(o1_t, o2_t)

    def test_object_type(self):
        l_a1_t = types.NominalType('A')
        l_k1_t = types.NominalType('B')
        l_r_t = types.NominalType('C')
        l_m1_t = types.MethodType([l_a1_t], {'k1': l_k1_t}, l_r_t)
        l_o_t = types.ObjectType({'m1': l_m1_t})
        r_a1_t = types.NominalType('A')
        r_k1_t = types.NominalType('B')
        r_r_t = types.NominalType('C')
        r_m1_t = types.MethodType([r_a1_t], {'k1': r_k1_t}, r_r_t)
        r_o_t = types.ObjectType({'m1': r_m1_t})
        self.assertEqual(l_o_t, r_o_t)
