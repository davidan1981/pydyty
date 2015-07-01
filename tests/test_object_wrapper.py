from base_test import BaseTestCase
from pydyty.object_wrapper import ObjectWrapper
from pydyty import types


class TestOldClass:
    def plus(self, x, y):
        return x + y

    def minus(self, x, y):
        return x - y


class TestClassA(object):

    def plus(self, x, y):
        return x + y

    def minus(self, x, y):
        return x - y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, rhs):
        self._x = rhs + 1


class TestClassB(object):

    def foo(self, a_1, a_2):
        return a_1.x + a_2.x

    def bar(self, first=None, second=None):
        return first.x + second.x

    def baz(self, first=0, second=0):
        return first + second


class ObjectWrapperTestCase(BaseTestCase):

    def setUp(self):
        super(ObjectWrapperTestCase, self).setUp()
        self.obj = TestClassA()
        self.obj_wrapper = ObjectWrapper(self.obj)

    def tearDown(self):
        super(ObjectWrapperTestCase, self).tearDown()

    def test_no_wrapping_twice(self):
        obj_wrapper = ObjectWrapper(self.obj_wrapper)
        self.assertIsNotNone(obj_wrapper)

    def test_primitive(self):
        obj_wrapper = ObjectWrapper(1)
        self.assertEqual('int', str(obj_wrapper.__pydyty_type__))

    def test_old_class_style(self):
        x = 1
        y = 2
        obj_wrapper = ObjectWrapper(TestOldClass())
        obj_wrapper.plus(x, y)
        obj_type = obj_wrapper.__pydyty_type__
        self.assertEqual('[plus: (int, int) -> int]', str(obj_type))

    def test_internal_properties(self):
        self.assertTrue(self.obj_wrapper.__pydyty__)
        self.assertEqual(self.obj, self.obj_wrapper.__pydyty_obj__)
        self.assertEqual(types.ObjectType(), self.obj_wrapper.__pydyty_type__)

    def test_one_method_call(self):
        x = 1
        y = 2
        self.obj_wrapper.plus(x, y)
        obj_type = self.obj_wrapper.__pydyty_type__
        self.assertEqual('[plus: (int, int) -> int]', str(obj_type))

    def test_two_method_calls(self):
        self.obj_wrapper.plus(1, 2)
        self.obj_wrapper.plus("a", "b")
        self.obj_wrapper.minus(1, 2)
        obj_type = self.obj_wrapper.__pydyty_type__
        exp_obj_type = types.ObjectType({
            'plus': types.IntersectionType([
                types.MethodType([
                    types.NominalType(1, is_object=True),
                    types.NominalType(2, is_object=True),
                ], [], types.NominalType(3, is_object=True)),
                types.MethodType([
                    types.NominalType("a", is_object=True),
                    types.NominalType("b", is_object=True),
                ], [], types.NominalType("ab", is_object=True)),
            ]),
            'minus': types.MethodType([
                types.NominalType(1, is_object=True),
                types.NominalType(2, is_object=True)
            ], [], types.NominalType(-1, is_object=True))
        })
        self.assertEqual(exp_obj_type, obj_type)

    def test_property_getter(self):
        self.obj_wrapper.x = 10
        self.assertEqual(11, self.obj_wrapper.x)
        obj_type = self.obj_wrapper.__pydyty_type__
        self.assertEqual('[x: int]', str(obj_type))

    def test_obj_wrapper_as_arg(self):
        a_1 = ObjectWrapper(TestClassA())
        a_2 = ObjectWrapper(TestClassA())
        b = ObjectWrapper(TestClassB())
        a_1.x = 1
        a_2.x = 2
        b.foo(a_1, a_2)
        self.assertEqual('[foo: ([x: int], [x: int]) -> int]',
                         str(b.__pydyty_type__))

    def test_obj_wrapper_as_kwarg(self):
        a_1 = ObjectWrapper(TestClassA())
        a_2 = ObjectWrapper(TestClassA())
        b = ObjectWrapper(TestClassB())
        a_1.x = 1
        a_2.x = 2
        b.bar(first=a_1, second=a_2)
        self.assertEqual('[bar: (first:[x: int], second:[x: int]) -> int]',
                         str(b.__pydyty_type__))
        b.baz(first=1, second=2)
        self.assertEqual('[bar: (first:[x: int], second:[x: int]) -> int,' +
                         ' baz: (first:int, second:int) -> int]',
                         str(b.__pydyty_type__))
