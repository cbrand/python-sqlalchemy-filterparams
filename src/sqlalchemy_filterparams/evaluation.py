# -*- encoding: utf-8 -*-

from sqlalchemy import and_, or_, not_, asc, desc

from filterparams.obj import (
    Parameter,
    BindingOperation,
    And,
    Or,
    Not,
)

from .util import convert


class Evaluation:

    def __init__(self,
                 query_config):
        self.query_config = query_config

    @property
    def query(self):
        return self.query_config.query

    def evaluate(self, sql_query):
        sql_query = self._apply_param_order(sql_query)
        sql_query = self._apply_sort(sql_query)
        return sql_query

    def _apply_param_order(self, sql_query):
        if self.query.param_order is not None:
            item, sql_query = self._process_param_item(
                self.query.param_order,
                sql_query,
            )

            sql_query = sql_query.filter(item)

        return sql_query

    def _process_param_item(self, item, sql_query):
        if isinstance(item, BindingOperation):
            return self._process_binding_item(item, sql_query)
        elif isinstance(item, Not):
            inner_item, sql_query = self._process_param_item(
                item.inner, sql_query,
            )
            return not_(inner_item), sql_query
        elif isinstance(item, Parameter):
            return self._process_parameter(item, sql_query)
        else:
            raise ValueError('Unknown parameter %s' % item)

    def _process_binding_item(self, item, sql_query):
        left_expression, sql_query = self._process_param_item(
            item.left,
            sql_query,
        )
        right_expression, sql_query = self._process_param_item(
            item.right,
            sql_query,
        )

        if isinstance(item, And):
            result = and_(
                left_expression,
                right_expression,
            )
        elif isinstance(item, Or):
            result = or_(
                left_expression,
                right_expression,
            )
        else:
            raise ValueError("Unkown param entry %s" % item)
        return result, sql_query

    def _process_parameter(self, item, sql_query):
        expressions = self.query_config.expressions
        sql_query, expression = expressions.get_filter_expression(
            sql_query,
            item.name
        )
        value = convert(
            item.value,
            expression.type,
            self.query_config.converters
        )
        filter_obj = self.query_config.filter_for(item.filter)
        return filter_obj(expression, value), sql_query

    def _apply_sort(self, sql_query):
        expressions = self.query_config.expressions

        orders = []
        for sort_item in self.query.orders:
            sort_func = asc
            if sort_item.direction == 'desc':
                sort_func = desc
            sql_query, expression = expressions.get_filter_expression(
                sql_query,
                sort_item.name
            )
            orders.append(sort_func(expression))
        return sql_query.order_by(*orders)
