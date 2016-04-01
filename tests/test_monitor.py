from base_test import BaseTestCase
from pydyty.monitor import Monitored


class MonitorTestCase(BaseTestCase):

    def test_monitor(self):

        class A(Monitored):
            def foo(self, x):
                return x

            # This doesn't work yet.
            def bar(self, x, y):
                return x + y

        a = A()
        self.assertEqual(1, a.foo(1))
        self.assertEqual('[foo: (int) -> int]',
                         str(A.__pydyty_type__))
        self.assertEqual(2, a.bar(1, 1))
        self.assertEqual("[bar: (int, int) -> int, foo: (int) -> int]",
                         str(A.__pydyty_type__))
