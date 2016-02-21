# -*- encoding: utf-8 -*-

import inspect

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from dateutil.parser import parse
from sqlalchemy import (
    Integer,
    Date,
    DateTime,
    Numeric,
    Float,
    Time,
)


def parse_date(date_string):
    return parse_datetime(date_string).date()


def parse_datetime(dt_string):
    if isinstance(dt_string, str):
        dt_string = parse(dt_string, fuzzy=False)
    if isinstance(dt_string, date) and not isinstance(dt_string, datetime):
        dt_string = datetime(
            dt_string.year, dt_string.month, dt_string.day
        )
    return dt_string


def parse_time(time_string):
    return parse_datetime(time_string).time()


def parse_decimal(decimal_string):
    try:
        return Decimal(decimal_string)
    except InvalidOperation as exception:
        raise ValueError(exception)


DEFAULT_CONVERTERS = {
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
    conversion_dict = conversion_dict or DEFAULT_CONVERTERS

    for type_cl, converter in conversion_dict.items():
        if is_type(column_type, type_cl):
            return converter(value)
    return value
