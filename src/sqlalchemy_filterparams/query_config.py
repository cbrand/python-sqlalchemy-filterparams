# -*- encoding: utf-8 -*-

from .filters import DEFAULT_FILTERS
from .util import DEFAULT_CONVERTERS


class QueryConfig:

    def __init__(self):
        self.model = None
        self.expressions = None
        self.session = None
        self._converters = None
        self.converters = None
        self._filters = None
        self.filters = None
        self.query = None

    @property
    def converters(self):
        return self._converters

    @converters.setter
    def converters(self, value):
        if value is None:
            value = DEFAULT_CONVERTERS.copy()
        self._converters = value

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, value):
        if value is None:
            value = DEFAULT_FILTERS
        self._filters = dict(
            (filter_obj.name, filter_obj)
            for filter_obj in value
        )

    def filter_for(self, filter_name):
        if filter_name not in self._filters:
            raise KeyError('Filter %s not found' % filter_name)
        filter_cl = self._filters[filter_name]
        return filter_cl(self.converters)
