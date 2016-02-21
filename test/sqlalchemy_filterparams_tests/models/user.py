# -*- encoding: utf-8 -*-

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    Date,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    fullname = Column(Unicode)
    date_of_birth = Column(Date)
    created_at = Column(DateTime)

    email_id = Column(Integer, ForeignKey('email.id'))
    email = relationship('EMail')
