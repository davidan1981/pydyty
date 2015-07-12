import inspect
import traceback
from base_test import BaseTestCase
from pydyty.loc import _SingleLocation, Location

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

class LocationTestCase(BaseTestCase):

    def test_single_loc(self):
        loc = _SingleLocation.create(traceback.extract_stack()[-1])
        self.assertEqual(__file__, loc.file)
        self.assertEqual(lineno() - 2, loc.line)
        self.assertEqual('test_single_loc', loc.func)
        self.assertEqual('loc = _SingleLocation.create(traceback.extract_stack()[-1])', loc.code)  # noqa

    def test_loc(self):
        loc = Location.create(traceback.extract_stack()[-1])
        self.assertEqual(__file__, loc[0].file)
        self.assertEqual(__file__, loc.first.file)
        loc.add_trace_slice(('foo', 123, 'bar', 'x = 1'))
        self.assertEqual('foo', loc.last.file)
        self.assertEqual(123, loc.last.line)
        self.assertEqual('bar', loc.last.func)
        self.assertEqual('x = 1', loc.last.code)
        loc2 = Location.create(traceback.extract_stack()[-1])
        loc2.add_trace_slice(('baz', 987, 'foo', 'y = 1'))
        loc.add_loc(loc2)
        self.assertEqual('baz', loc.last.file)
        self.assertEqual(987, loc.last.line)
        self.assertEqual('foo', loc.last.func)
        self.assertEqual('y = 1', loc.last.code)
