# -*- encoding: utf-8 -*-

from sqlalchemy.orm import (
    aliased,
)


class ExpressionHandler:
    def __init__(self, lookup, model):
        self.lookup = lookup
        self.model = model
        self._join_cache = {}

    def _base_obj(self, name):
        return ExpressionItem(
            self.lookup[name]
        )

    def get_filter_expression(self, query, name):
        join_path = self.path_to(name)
        query = self._evaluate_join_path(
            query,
            join_path,
        )
        param = self.param_of(name)
        return query, param

    def param_of(self, name):
        param = self._base_obj(name).param
        join_path = self.path_to(name)
        if join_path in self._join_cache:
            base_obj = self._join_cache[join_path]
        else:
            base_obj = self.model
        if hasattr(param, 'property'):
            property_key = param.property.key
        else:
            property_key = param

        return getattr(base_obj, property_key)

    def path_to(self, name):
        return self._base_obj(name).join_path

    def _evaluate_join_path(self, query, path):
        evaluated_path = []
        current_base = self.model
        for path_item in path:
            evaluated_path.append(path_item)
            current_path = tuple(evaluated_path)
            if current_path not in self._join_cache:
                relation = getattr(
                    current_base,
                    path_item,
                    None
                )
                if (not hasattr(relation, 'property') or
                        not hasattr(relation.property, 'mapper') or
                        not hasattr(
                            relation.property.mapper, 'class_')):
                    raise ValueError(
                        (
                            'The specified join path '
                            'from the base obj %s has a '
                            'join configuration in %s '
                            'which is not a relationship.'
                        ) % (current_base, path_item)
                    )

                join_cl = relation.property.mapper.class_
                aliased_join_cl = aliased(join_cl)
                query = query.join(aliased_join_cl, relation)

                self._join_cache[current_path] = aliased_join_cl
            current_base = self._join_cache[current_path]
        return query


class ExpressionItem:
    def __init__(self, data):
        self._data = data

    @property
    def join_path(self):
        if isinstance(self._data, dict):
            join_path = self._data.get('join', None)
        else:
            join_path = None

        if join_path is None:
            return tuple()
        elif isinstance(join_path, str):
            join_path = (join_path,)
        return join_path

    @property
    def param(self):
        if not isinstance(self._data, dict):
            return self._data
        return self._data.get('param', None)
