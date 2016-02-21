# -*- encoding: utf-8 -*-

from sqlalchemy import String

from .util import convert, is_type


class Filter:
    name = None

    def __init__(self, converters):
        self.converters = converters

    def __eq__(self, other):
        if isinstance(other, Filter):
            return other.name == self.name
        elif isinstance(other, str):
            return self.name == other
        else:
            super().__eq__(other)

    def __call__(self, param, value):
        return self.apply(param, value)

    def apply(self, param, value):
        if hasattr(param, 'type'):
            type_cl = param.type
        else:
            type_cl = param
        value = self._convert(type_cl, value)
        return self._apply(param, value)

    def _convert(self, type_cl, value):
        return convert(value, type_cl, self.converters)


class EqFilter(Filter):
    name = 'eq'

    def _apply(self, param, value):
        return param == value


class NeqFilter(Filter):
    name = 'neq'

    def _apply(self, param, value):
        return param != value


class LesserFilter(Filter):
    name = 'lt'

    def _apply(self, param, value):
        return param < value


class LesserEqualFilter(Filter):
    name = 'lte'

    def _apply(self, param, value):
        return param <= value


class GreaterFilter(Filter):
    name = 'gt'

    def _apply(self, param, value):
        return param > value


class GreaterEqualFilter(Filter):
    name = 'gte'

    def _apply(self, param, value):
        return param >= value


class _LikeBase(Filter):
    def apply(self, param, value):
        if not is_type(param.type, String):
            raise ValueError(
                'Like is only possible on string'
            )
        return super().apply(param, value)


class LikeFilter(_LikeBase):
    name = 'like'

    def _apply(self, param, value):
        return param.like(value)


class ILikeFilter(_LikeBase):
    name = 'ilike'

    def _apply(self, param, value):
        return param.ilike(value)


DEFAULT_FILTERS = [
    EqFilter,
    NeqFilter,
    LesserFilter,
    LesserEqualFilter,
    GreaterFilter,
    GreaterEqualFilter,
    LikeFilter,
    ILikeFilter,
]
