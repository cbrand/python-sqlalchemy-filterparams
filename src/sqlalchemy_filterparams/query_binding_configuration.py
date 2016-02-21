# -*- encoding: utf-8 -*-

from filterparams import build_parser
from filterparams.obj import Query

from .evaluation import Evaluation
from .expression import ExpressionHandler
from .filters import DEFAULT_FILTERS
from .query_config import QueryConfig


class QueryBindingConfiguration:

    __config__ = {
        'for': None,
        'sessionmaker': None,
        'binding': {},
        'converters': None,
        'filters': None,
        'default_filter': None,
    }

    def __init__(self, session=None):
        self.__cached_model = None
        self._session = session

    @classmethod
    def model(cls):
        configuration = getattr(cls, '__config__')
        model = None

        if configuration and configuration.get('for', None) is not None:
            model = configuration['for']
        else:
            for model_cl in cls.__bases__:
                model_present = getattr(model_cl, 'model', None)
                if model_present and callable(model_cl.model):
                    model = model_cl.model()

                if model is not None:
                    break

        return model

    @classmethod
    def config_entry(cls, name):
        candidates = [cls]
        seen = set()

        for candidate in candidates:
            if candidate in seen:
                continue
            seen.add(candidate)

            if hasattr(candidate, '__config__'):
                config = candidate.__config__
                if name in config:
                    return config[name]
            else:
                pass

            candidates.extend(cls.__bases__)

    @property
    def _cached_model(self):
        if getattr(self, '__cached_model', None) is None:
            self.__cached_model = self.model()
        return self.__cached_model

    @property
    def session(self):
        if self._session is not None:
            return self._session
        else:
            return self._session_from_config

    @property
    def _session_from_config(self):
        sessionmaker = self.config_entry('sessionmaker')
        if callable(sessionmaker):
            return sessionmaker()
        else:
            return sessionmaker

    @property
    def expression_handler(self):
        return ExpressionHandler(
            self.config_entry('binding'),
            self.model(),
        )

    @property
    def _base_query(self):
        if self._cached_model is None:
            raise RuntimeError(
                'Could not determine model '
                'for query binding configuration %s' % self.__class__
            )
        if hasattr(self._cached_model, 'query'):
            query = self._cached_model.query()
        elif self.session is not None:
            query = self.session.query(self._cached_model)
        else:
            raise RuntimeError(
                'Could not access SQLAlchemy session. Please '
                'provide a \'session\' in the constructor.'
            )

        return query

    @property
    def _filters(self):
        return self.config_entry('filters') or DEFAULT_FILTERS

    @property
    def _default_filter(self):
        return self.config_entry('default_filter') or 'eq'

    @property
    def _filter_names(self):
        return [
            filter_obj.name
            for filter_obj in self._filters
        ]

    def evaluate_params(self, params):
        parser = build_parser(self._filter_names, self._default_filter)
        return self.evaluate(parser(params))

    def evaluate(self, filterparams_query: Query):
        return Evaluation(
            self.config_with(filterparams_query)
        ).evaluate(self._base_query)

    def config_with(self, query):
        query_config = QueryConfig()
        query_config.query = query
        query_config.converters = self.config_entry('converters')
        query_config.filters = self.config_entry('filters')
        query_config.session = self.session
        query_config.model = self.model()
        query_config.expressions = self.expression_handler
        return query_config
