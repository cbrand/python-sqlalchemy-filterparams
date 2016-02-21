# -*- encoding: utf-8 -*-

from filterparams.obj import Query
from .evaluation import Evaluation
from .expression import ExpressionHandler
from .query_config import QueryConfig


class QueryBindingConfiguration:

    __config__ = {
        'for': None,
        'sessionmaker': None,
        'binding': {},
        'joins' : {},
        'converters': None,
        'filters': None,
    }

    def __init__(self, **kwargs):
        self.__cached_model = None
        self._session = kwargs.get('session', None)

    @classmethod
    def model(cls):
        configuration = getattr(cls, '__config__')
        model = None

        if configuration and configuration.get('for', None) is not None:
            model = configuration['for']
        else:
            for cl in cls.__bases__:
                if getattr(cl, 'model', None) and callable(cl.model):
                    model = cl.model()

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

            if hasattr(cls, '__config__'):
                config = cls.__config__
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
            self.config_entry('joins'),
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

    def evaluate(self, filterparams_query: Query):
        Evaluation(
            self.config_with(filterparams_query)
        ).evaluate(filterparams_query)

    def config_with(self, query):
        query_config = QueryConfig()
        query_config.query = query
        query_config.converters = self.config_entry('converters')
        query_config.filters = self.config_entry('filters')
        query_config.session = self.session
        query_config.model = self.model()
        query_config.expressions = self.expression_handler
        return query_config
