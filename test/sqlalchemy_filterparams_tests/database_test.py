# -*- encoding: utf-8 -*-

from unittest import TestCase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_filterparams_tests.models import (
    Base,
)


class BaseDatabaseTest(TestCase):

    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    session = Session()

    def setUp(self):
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

