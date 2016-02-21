# -*- encoding: utf-8 -*-

from expects import *

from datetime import date, datetime

from filterparams.obj import (
    Query,
    And,
    Or,
    Not,
    Order,
    BindingOperation,
)

from sqlalchemy_filterparams.expression import (
    ExpressionHandler,
)
from sqlalchemy_filterparams.evaluation import (
    Evaluation
)
from sqlalchemy_filterparams.query_config import (
    QueryConfig
)

from sqlalchemy_filterparams_tests.models import (
    Domain,
    EMail,
    User,
)
from sqlalchemy_filterparams_tests.database_test import (
    BaseDatabaseTest
)


class EvaluationTest(BaseDatabaseTest):

    def setUp(self):
        super().setUp()
        self.session.add(User(
            name='user',
            fullname='The User',
            date_of_birth=date(1985, 10, 26),
            created_at=datetime(2015, 10, 21),
        ))
        self.session.commit()
        self.sql_query = self.session.query(User)
        self.query_config = QueryConfig()
        self.query_config.model = User
        self.query_config.expressions = ExpressionHandler({
            'name': User.name,
            'fullname': User.fullname,
            'birth_date': User.date_of_birth,
            'created_at': User.created_at,
            'mail': {
                'param': 'mail',
                'join': 'email'
            },
            'mail.domain': {
                'param': Domain.domain,
                'join': ('email', 'domain'),
            },
            'fullname.not_existing': {
                'param': 'not_existing',
                'join': ('fullname',)
            }
        }, User)
        self.query = Query()

    @property
    def evaluation(self):
        return Evaluation(self.query_config)

    @property
    def evaluated_qry(self):
        return self.evaluation.evaluate(self.sql_query)

    @property
    def evaluated_names(self):
        return [item.name for item in self.evaluated_qry]

    @property
    def query(self) -> Query:
        return self.query_config.query

    @query.setter
    def query(self, value):
        self.query_config.query = value

    def test_filter_application_eq(self):
        self.query.add('name', filter='eq', value='user')
        self.query.param_order = self.query.get_param('name')
        expect(self.evaluated_qry.first()).to_not(be_none)

    def test_filter_application_neq(self):
        self.query.add('name', filter='neq', value='user')
        self.query.param_order = self.query.get_param('name')
        expect(self.evaluated_qry.first()).to(be_none)

    def test_filter_application_gt(self):
        self.query.add('birth_date', filter='gt', value='1985-10-26')
        self.query.param_order = self.query.get_param('birth_date')
        expect(self.evaluated_qry.first()).to(be_none)

    def test_filter_application_gt_match(self):
        self.query.add('birth_date', filter='gt', value='1985-10-25')
        self.query.param_order = self.query.get_param('birth_date')
        expect(self.evaluated_qry.first()).to_not(be_none)

    def test_filter_application_gte(self):
        self.query.add('birth_date', filter='gte', value='1985-10-27')
        self.query.param_order = self.query.get_param('birth_date')
        expect(self.evaluated_qry.first()).to(be_none)

    def test_filter_application_gte_match(self):
        self.query.add('birth_date', filter='gte', value='1985-10-26')
        self.query.param_order = self.query.get_param('birth_date')
        expect(self.evaluated_qry.first()).to_not(be_none)

    def test_filter_application_lt(self):
        self.query.add('birth_date', filter='lt', value='1985-10-26')
        self.query.param_order = self.query.get_param('birth_date')
        expect(self.evaluated_qry.first()).to(be_none)

    def test_filter_application_lt_match(self):
        self.query.add('birth_date', filter='lt', value='1985-10-27')
        self.query.param_order = self.query.get_param('birth_date')
        expect(self.evaluated_qry.first()).to_not(be_none)

    def test_filter_application_lte(self):
        self.query.add('birth_date', filter='lte', value='1985-10-25')
        self.query.param_order = self.query.get_param('birth_date')
        expect(self.evaluated_qry.first()).to(be_none)

    def test_filter_application_lte_match(self):
        self.query.add('birth_date', filter='lte', value='1985-10-26')
        self.query.param_order = self.query.get_param('birth_date')
        expect(self.evaluated_qry.first()).to_not(be_none)

    def test_filter_application_like(self):
        self.query.add('fullname', filter='like', value='The%')
        self.query.param_order = self.query.get_param('fullname')
        expect(self.evaluated_qry.first()).to_not(be_none)

    def test_filter_application_like_no_match(self):
        self.query.add('fullname', filter='like', value='%The')
        self.query.param_order = self.query.get_param('fullname')
        expect(self.evaluated_qry.first()).to(be_none)

    def test_filter_application_ilike(self):
        self.query.add('fullname', filter='ilike', value='the%')
        self.query.param_order = self.query.get_param('fullname')
        expect(self.evaluated_qry.first()).to_not(be_none)

    def test_filter_and(self):
        self.query.add('fullname', filter='eq', value='The User')
        self.query.add('name', filter='eq', value='user2')
        self.query.param_order = And(
            self.query.get_param('fullname'),
            self.query.get_param('name'),
        )
        expect(self.evaluated_qry.first()).to(be_none)

    def test_filter_or(self):
        self.query.add('fullname', filter='eq', value='The User')
        self.query.add('name', filter='eq', value='user2')
        self.query.param_order = Or(
            self.query.get_param('fullname'),
            self.query.get_param('name'),
        )
        expect(self.evaluated_qry.first()).to_not(be_none)

    def test_filter_not(self):
        self.query.add('name', filter='eq', value='user')
        self.query.param_order = Not(self.query.get_param('name'))
        expect(self.evaluated_qry.first()).to(be_none)

    def add_user_order(self):
        self.session.add(User(
            name='abc',
            fullname='The User',
            date_of_birth=date(1985, 10, 26),
            created_at=datetime(2015, 10, 21),
        ))
        self.session.commit()

    def test_order(self):
        self.add_user_order()

        self.query.orders = [Order('name')]
        expect(self.evaluated_names).to(contain_exactly('abc', 'user'))

    def test_order_desc(self):
        self.add_user_order()

        self.query.orders = [Order('name', 'desc')]
        expect(self.evaluated_names).to(contain_exactly('user', 'abc'))

    def test_join(self):
        user = self.sql_query.first()
        user.email = EMail(
            mail='test@example.com',
            domain=Domain(
                domain='example.com',
            )
        )
        self.session.commit()
        self.query.add('mail.domain', filter='neq', value='example.com')
        self.query.param_order = self.query.get_param('mail.domain')
        expect(self.evaluated_qry.first()).to(be_none)

    def test_like_on_no_string(self):
        self.query.add('created_at', filter='like', value='2016')
        self.query.param_order = self.query.get_param('created_at')
        expect(lambda: self.evaluated_qry).to(raise_error(ValueError))

    def test_error_on_unknown_param(self):
        self.query.param_order = lambda: '123'
        expect(lambda: self.evaluated_qry).to(raise_error(ValueError))

    def test_unknown_binding_param_item(self):
        class UnknownBinding(BindingOperation):
            pass

        self.query.add('name', filter='eq', value='user')
        name_param = self.query.get_param('name')
        self.query.param_order = UnknownBinding(name_param, name_param)
        expect(lambda: self.evaluated_qry).to(raise_error(ValueError))

    def test_string_binding_config(self):
        user = self.sql_query.first()
        user.email = EMail(
            mail='test@example.com',
            domain=Domain(
                domain='example.com',
            )
        )
        self.session.commit()
        self.query.add('mail', filter='eq', value='test@example.com')
        self.query.param_order = self.query.get_param('mail')
        expect(self.evaluated_qry.first()).to_not(be_none)

    def test_fullname_not_existing_relationship(self):
        self.query.add('fullname.not_existing',
                       filter='eq', value='test@example.com')
        self.query.param_order = self.query.get_param(
            'fullname.not_existing')
        expect(lambda: self.evaluated_qry).to(raise_error(ValueError))
