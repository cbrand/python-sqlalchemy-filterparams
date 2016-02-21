# -*- encoding: utf-8 -*-

from expects import *

from sqlalchemy import Integer
from sqlalchemy_filterparams.filters import (
    EqFilter,
    NeqFilter,
)


def test_identification_by_str():
    expect(EqFilter(None)).to(equal('eq'))


def test_negative_identification_by_str():
    expect(EqFilter(None)).to_not(equal('neq'))


def test_identification_by_obj():
    expect(EqFilter(None)).to(equal(EqFilter(None)))


def test_negative_identification_by_obj():
    expect(EqFilter(None)).to_not(equal(NeqFilter(None)))


def test_negative_identification_by_other():
    expect(EqFilter(None)).to_not(equal(1))


def test_apply_with_type():
    EqFilter(None).apply(Integer, '1')
