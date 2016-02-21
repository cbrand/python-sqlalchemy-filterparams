# -*- encoding: utf-8 -*-

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    ForeignKey
)
from sqlalchemy.orm import relationship

from .base import Base


class EMail(Base):
    __tablename__ = 'email'

    id = Column(Integer, primary_key=True)
    mail = Column(Unicode)
    domain_id = Column(Integer, ForeignKey('domain.id'))

    domain = relationship('Domain')
