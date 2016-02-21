# -*- encoding: utf-8 -*-

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
)

from .base import Base


class Domain(Base):
    __tablename__ = 'domain'

    id = Column(Integer, primary_key=True)
    domain = Column(Unicode)
