# -*- encoding: utf-8 -*-

import inspect

from datetime import date, datetime

from dateutil.parser import parse
from decimal import Decimal, InvalidOperation
from sqlalchemy import (
    Integer,
    Date,
    DateTime,
    Numeric,
    Float,
    Time,
)


def parse_date(s):
    return parse_datetime(s).date()


def parse_datetime(s):
    if isinstance(s, str):
        s = parse(s, fuzzy=False)
    if isinstance(s, date) and not isinstance(s, datetime):
        s = datetime(s.year, s.month, s.day)
    return s


def parse_time(s):
    return parse_datetime(s).time()


def parse_decimal(s):
    try:
        return Decimal(s)
    except InvalidOperation as e:
        raise ValueError(e)


default_converters = {
    Integer: int,
    Numeric: parse_decimal,
    Float: float,
    Date: parse_date,
    DateTime: parse_datetime,
    Time: parse_time,
}


def is_type(column_type, to_check_type):
    return (
        isinstance(column_type, to_check_type) or
        (
            inspect.isclass(to_check_type) and
            inspect.isclass(column_type) and
            issubclass(column_type, to_check_type)
        ) or
        column_type is to_check_type
    )


def convert(value, column_type, conversion_dict=None):
    conversion_dict = conversion_dict or default_converters

    for type_cl, converter in conversion_dict.items():
        if is_type(column_type, type_cl):
            return converter(value)
    return value
