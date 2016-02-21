# -*- encoding: utf-8 -*-

from datetime import date, datetime

from expects import *

from sqlalchemy_filterparams.query_binding_configuration import (
    QueryBindingConfiguration
)

from sqlalchemy_filterparams_tests.database_test import BaseDatabaseTest
from sqlalchemy_filterparams_tests.models import (
    Domain,
    EMail,
    User,
)


class QueryBindingConfigurationTest(BaseDatabaseTest):

    def create_cl(self):
        class Config(QueryBindingConfiguration):
            __config__ = {
                'for': User,
                'sessionmaker': self.Session,
                'binding': {
                    'name': 'name',
                    'fullname': 'fullname',
                    'birth_date': 'date_of_birth',
                    'created_at': 'created_at',
                    'mail': {
                        'param': 'mail',
                        'join': 'email'
                    },
                    'mail.domain': {
                        'param': 'domain',
                        'join': ('email', 'domain'),
                    },
                    'fullname.not_existing': {
                        'param': 'not_existing',
                        'join': ('fullname',)
                    }
                }
            }
        return Config

    def setUp(self):
        super().setUp()
        self.config_cl = self.create_cl()
        self.session.add(User(
            name='user',
            fullname='The User',
            date_of_birth=date(1985, 10, 26),
            created_at=datetime(2015, 10, 21),
            email = EMail(
                mail='test@example.com',
                domain=Domain(
                    domain='example.com',
                )
            )
        ))
        self.session.commit()

    def test_empty_evaluation(self):
        query = self.config_cl().evaluate_params({})
        expect(len(query.all())).to(equal(1))

    def test_query_evaluation(self):
        query = self.config_cl().evaluate_params({
            'filter[name][eq]': 'user'
        })
        expect(query.first()).to_not(be_none)

    def delete_session(self):
        del self.config_cl.__config__['sessionmaker']

    def test_error_if_no_session(self):
        self.delete_session()
        expect(lambda: self.config_cl().evaluate_params({
            'filter[name][eq]': 'user'
        })).to(raise_error(RuntimeError))

    def test_evaluation_with_provided_session(self):
        self.delete_session()
        query = self.config_cl(self.session).evaluate_params({
            'filter[name][eq]': 'user'
        })
        expect(query.first()).to_not(be_none)

    def test_nested_config(self):
        class NestedConfig(self.config_cl):
            __config__ = {}

        query = NestedConfig().evaluate_params({})
        expect(query.first()).to_not(be_none)

    def test_error_on_no_provided_model(self):
        del self.config_cl.__config__['for']
        expect(lambda: self.config_cl().evaluate_params({})).to(
            raise_error(RuntimeError))
