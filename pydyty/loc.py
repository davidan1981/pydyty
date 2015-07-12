class _SingleLocation(object):
    """ Represents a single location. Do not use this directly outside of
    this module. The purpose is to represent a single stack trace slice,
    which consists of file, line, func, and code."""

    def __init__(self, **kwargs):
        self.file = kwargs.get('file')
        self.line = kwargs.get('line')
        self.func = kwargs.get('func')
        self.code = kwargs.get('code')

    @classmethod
    def create(cls, trace_slice):
        return cls(
            file=trace_slice[0],
            line=trace_slice[1],
            func=trace_slice[2],
            code=trace_slice[3]
        )


class Location(object):
    """ Represents a location which may consist of an actual code location
    or a list of multiple code locations."""

    def __init__(self):
        self.locs = []

    def __getitem__(self, i):
        return self.locs[i]

    @property
    def first(self):
        return self.locs[0]

    @property
    def last(self):
        return self.locs[-1]

    @classmethod
    def create(cls, trace_slice):
        loc = cls()
        loc.add_trace_slice(trace_slice)
        return loc

    def add_loc(self, loc):
        self.locs.extend(loc.locs)

    def add_trace_slice(self, trace_slice):
        self.locs.append(_SingleLocation.create(trace_slice))
