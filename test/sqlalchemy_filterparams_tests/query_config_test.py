# -*- encoding: utf-8 -*-

from expects import *

from sqlalchemy import Integer

from sqlalchemy_filterparams.filters import (
    EqFilter,
    default_filters,
)
from sqlalchemy_filterparams.util import (
    default_converters
)
from sqlalchemy_filterparams.query_config import (
    QueryConfig
)


def test_use_default_filters():
    config_filters = list(QueryConfig().filters.values())
    expect(len(config_filters)).to(equal(len(default_filters)))

    for filter_obj in config_filters:
        expect(default_filters).to(contain(filter_obj))


def test_set_filters():
    query_filter = QueryConfig()
    query_filter.filters = [EqFilter]
    config_filters = list(query_filter.filters.values())
    expect(config_filters).to(contain_exactly(EqFilter))


def test_use_default_converters():
    expect(QueryConfig().converters).to(equal(default_converters))


def test_set_converters():
    query_filter = QueryConfig()
    query_filter.converters = {
        Integer: int
    }
    expect(query_filter.converters).to(equal({
        Integer: int
    }))


def test_not_existent_filter():
    query_filter = QueryConfig()
    expect(lambda: query_filter.filter_for('not_existing')).to(
        raise_error(KeyError))
