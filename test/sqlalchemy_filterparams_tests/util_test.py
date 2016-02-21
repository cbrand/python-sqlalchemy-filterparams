# -*- encoding: utf-8 -*-

from expects import *

from datetime import datetime, date, time
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    DECIMAL,
    Float,
    Integer,
    Numeric,
    Unicode,
    Time,
)

from sqlalchemy_filterparams.util import is_type, convert


def test_is_type_class():
    assert is_type(Integer, Integer)


def test_is_not_type_class():
    assert not is_type(Integer, Numeric)


def test_is_type_instance():
    assert is_type(Integer(), Integer)


def test_is_not_type_instance():
    assert not is_type(Integer(), Numeric)


def test_is_type_class_subclass():
    assert is_type(Float, Numeric)


def test_convert_integer():
    expect(convert('3', Integer)).to(equal(3))


def test_no_convert_string():
    expect(convert('3.0', Unicode)).to(equal('3.0'))


def test_convert_decimal():
    expect(convert('3.0', DECIMAL)).to(equal(Decimal('3.0')))


def test_convert_float():
    expect(convert('3', Float)).to(equal(3.0))


def test_convert_float_error():
    expect(lambda: convert('a', Float)).to(raise_error(ValueError))


def test_convert_decimal_error():
    expect(lambda: convert('3a', DECIMAL)).to(raise_error(ValueError))


def test_convert_integer_error():
    expect(lambda: convert('3b', Integer)).to(raise_error(ValueError))


def test_convert_time():
    expect(convert('4:00', Time)).to(equal(time(4,0)))


def test_convert_time_unparseable():
    expect(lambda: convert('4:asdf', Time)).to(raise_error(ValueError))


def test_convert_date():
    expect(convert('2016-01-01', Date)).to(equal(date(2016, 1, 1)))


def test_convert_date_unparseable():
    expect(lambda: convert('2016-ab-01', Date)).to(
        raise_error(ValueError))


def test_convert_datetime():
    expect(convert('2016-01-01 18:00:00', DateTime)).to(equal(
        datetime(2016, 1, 1, 18, 0, 0)))


def test_convert_datetime_reverse():
    expect(convert('18:00:00 2016-01-01', DateTime)).to(equal(
        datetime(2016, 1, 1, 18, 0, 0)))


def test_convert_datetime_unparseable():
    expect(lambda: convert('2016-01-01 ab:cd:ef', DateTime)).to(
        raise_error(ValueError))


def test_custom_converter():
    class SomeStuff:
        pass

    expect(convert('random', SomeStuff, {
        SomeStuff: lambda data: '%s stuff' % data
    })).to(equal('random stuff'))
