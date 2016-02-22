# SQLAlchemy Filterparams #

This is a library which uses the syntax available through the 
[filterparams](https://github.com/cbrand/python-filterparams) 
([PyPi](https://pypi.python.org/pypi/filterparams)) package and 
maps it on top of SQLAlchemy.

It can be used to integrate query capabilities to RESTful APIs.

## Installation ##

The project is available on [pypi](https://pypi.python.org/pypi/sqlalchemy-filterparams). 
Just use `pip install sqlalchemy-filterparams` to install it. Alternatively
you can also use setuptools with `easy_install sqlalchemy-filterparams`.

## Usage ##

To apply any search parameters to the given URL you must first define
a binding configuration through subclassing the `QueryBinding` class.

It is recommended to have one global subclass in your project which
includes common functionality.

```python
from sqlalchemy import Integer

from sqlalchemy_filterparams import QueryBinding
from sqlalchemy_filterparams.filters import (
    EqFilter,
    NeqFilter,
)

from .model import DBSession

class BasicQueryBinding(QueryBinding):
    __config__ = {
        'filters': [EqFilter, NeqFilter],
        'converters': {
            Integer: int,
        },
        'default_filter': 'eq',
        'sessionmaker': DBSession,
    }
```

Some things to note here:
- The `default_filter` is always set per default to 'eq'. You can omit
  it if you want to keep it that way.
- Providing a `sessionmaker` is also optional and is a helper 
  functionality when you are working with 
  [SQLAlchemy's scoped/thread-local sessions](http://docs.sqlalchemy.org/en/latest/orm/contextual.html).
  You can also omit it, but you have to provide the session individually on each
  request.
- The `converters` map various functions to convert the query parameter strings
  to the python data type. This is a necessary step for supporting lesser/greater
  and other comparisons for the objects. The configured converters must be a dictionary
  with the columns type class as key and a function which expects one parameter as its
  value. This function should convert the passed string to the wanted format.
  If no conversion can be done a `ValueError` may be raised. If no converters are 
  specified the default ones are used. They are provide the converters for the following
  SQLAlchemy columns:
    - `Integer` - converting to `int`
    - `Numeric` - converting to `decimal.Decimal`
    - `Float` - converting to `float`
    - `Date` - converting to `datetime.date`
    - `DateTime` - converting to `datetime.datetime`
    - `Time` - converting to `datetime.time`
  The dates are parsed through the functionality provided by 
  [`python-dateutil`](https://pypi.python.org/pypi/python-dateutil/).
  You can access the default filters through 
  `sqlalchemy_filterparams.filters.DEFAULT_FILTERS`.
- The `filters` are the allowed filters for the query. These classes have
  to have a `name` parameter, which is used for identification.
  Per default the following filters are registered:
  <table>
    <thead>
      <tr>
        <th>Name</th><th>Filter name</th><th>Operation</th>
      </tr>
    </thead>
    <tbody>
        <tr>
          <td><pre>eq</pre></td>
          <td><pre>EqFilter</pre></td>
          <td><pre>key = value</pre></td>
        </tr>
        <tr>
          <td><pre>neq</pre></td>
          <td><pre>NeqFilter</pre></td>
          <td><pre>key != value</pre></td>
        </tr>
        <tr>
          <td><pre>lt</pre></td>
          <td><pre>LtFilter</pre></td>
          <td><pre>key < value</pre></td>
        </tr>
        <tr>
          <td><pre>lte</pre></td>
          <td><pre>LteFilter</pre></td>
          <td><pre>key <= value</pre></td>
        </tr>
        <tr>
          <td><pre>gt</pre></td>
          <td><pre>GtFilter</pre></td>
          <td><pre>key > value</pre></td>
        </tr>
        <tr>
          <td><pre>gte</pre></td>
          <td><pre>GteFilter</pre></td>
          <td><pre>key >= value</pre></td>
        </tr>
        <tr>
          <td><pre>like</pre></td>
          <td><pre>LikeFilter</pre></td>
          <td><pre>key LIKE value</pre></td>
        </tr>
        <tr>
          <td><pre>ilike</pre></td>
          <td><pre>ILikeFilter</pre></td>
          <td><pre>key ILIKE value</pre></td>
        </tr>
    </tbody>
  </table>

After this basic configuration is done you can configure a parser
for one specific model.

Given you have the following SQLAlchemy model structure:

```python
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    fullname = Column(Unicode)
    date_of_birth = Column(Date)
    created_at = Column(DateTime)

    email_id = Column(Integer, ForeignKey('email.id'))
    email = relationship('EMail')

class EMail(Base):
    __tablename__ = 'email'

    id = Column(Integer, primary_key=True)
    mail = Column(Unicode)
    domain_id = Column(Integer, ForeignKey('domain.id'))

    domain = relationship('Domain')

class Domain(Base):
    __tablename__ = 'domain'

    id = Column(Integer, primary_key=True)
    domain = Column(Unicode)
``

Then a definition would look like (given that the `BasicQueryBinding` class is present):

```python
class UserQueryBinding(BasicQueryBinding):
    __config__ = {
        'for': User,
        'binding': {
            'name': User.name,
            'fullname': User.fullname,
            'birth_date': User.date_of_birth,
            'created_at': 'created_at',
            'email': {
                'param': 'mail',
                'join': 'email',
            },
            'email.domain': {
                'param': Domain.domain,
                'join': ('email', 'domain'),
            },
        },
    }
```

The keys in the `binding` configuration is corresponding
to the names of the parameters which the API provides. These have
to be provided to the API as described in the 
[filterparams documentation](https://github.com/cbrand/python-filterparams).
The values is the information how to access the underlying model and
it's submodels. Please note, that it doesn't matter if you use the 
parameter name or the actual attribute object. If you want to provide
values which are behind a relationship you also have to define
it's join path. This is done by adding a dictionary and specifying the
parameter which should be accessed through the `param` key and the
relationships to traverse through the `join` key. The library is using
these information to correctly build the SQL query. It also does only
use the joins which are needed to fulfill the filter requirements.
In general you should limit the joins in your model if possible for
performance reasons. This is especially the case if the relationship
is going through 1:n and does query a huge data subset.
 
Finally, you also need to provide the `for` key and point to the
base model of the query.

To use your parser do:

```python
query = UserQueryBinding().evaluate_params({
    'filter[name][eq]': 'cbrand',
})
```

The `query` is the SQLAlchemy Query which is preconfigured with the
given filters. You can add other filters to the query and apply
`LIMIT` and `OFFSET` to it afterwards.

If you want to provide a session and thus not use the `sessionmaker` you
have to pass it in the constructor.

```python
query = UserQueryBinding(session).evaluate_params({})
```

## License ##

The project is licensed under 
[MIT](https://opensource.org/licenses/MIT).

## Used Libaries ##

The following libraries are used for achieving the described 
functionality.

- [SQLAlchemy](https://pypi.python.org/pypi/SQLAlchemy/) - For mapping the data onto SQL - Licensed under [MIT](https://github.com/zzzeek/sqlalchemy/blob/master/LICENSE).
- [filterparams](https://pypi.python.org/pypi/filterparams) - For parsing the query - Licensed under [MIT](https://github.com/cbrand/python-filterparams/blob/master/LICENSE.txt).
- [python-dateutil](https://pypi.python.org/pypi/python-dateutil/) - For parsing dates - Licensed under the [simplified BSD license](https://pypi.python.org/pypi/python-dateutil/). 
