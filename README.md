---
description: An introduction to the Marrow Mongo Document Mapper and overview of features.
---
# The Marrow Mongo Document Mapper

Marrow Mongo is a collection of small, focused utilities written to enhance use of the [PyMongo native MongoDB driver](http://api.mongodb.com/python/current/) without the overhead, glacial update cycle, complexity, and head-space requirements of a full *active record* object document mapper.

{% method -%}
## Features

##### Declarative document modeling.

Instantiate field objects and associate them with custom `Document` sub-classes to model your data declaratively.

```python
class Television(Document):
	model = String()
```

##### Refined, Pythonic _data access object_ interactions.

Utilize `Document` instances as attribute access mutable mappings with value typecasting, directly usable with PyMongo APIs. Attention is paid to matching Python language expectations, such as allowing instantiation using positional arguments. Values are always stored in the PyMongo-preferred MongoDB native format, and cast on attribute access as needed.

```python
document = Television('D50u-D1')
collection.insert_one(document)
```

##### Collection and index metadata and creation shortcuts.

Keep information about your data model with your data model and standardize access.

```python
class Television(Document):
	__collection__ = 'tv'
	model = String()
	_model = Index('model')

collection = Television.create_collection(database)
```

##### Filter construction through rich comparisons.

##### Parametric filter, projection, sort, and update document construction.

##### Advanced GeoJSON support.

##### Liberally MIT licensed.

{% common -%}
## Code Quality

##### 100% test coverage.

Guaranteed to be fully tested before any release. We utilize [Travis](https://travis-ci.org/marrow/mongo/) continuous integration reporting to [Codecov.io](https://codecov.io/gh/marrow/mongo/) for test coverage reporting. We also monitor requirements for security concerns and deprecation using [Requires.io](https://requires.io/github/marrow/mongo/requirements/?branch=master),

##### 100% code quality.

Extensive static analysis and proactive use of tools such as [pre-commit](http://pre-commit.com), with plugins [such as](https://github.com/marrow/mongo/blob/develop/.pre-commit-config.yaml) [OpenStack Bandit](https://wiki.openstack.org/wiki/Security/Projects/Bandit) infosec analyzer, and various linting tools, help to keep code maintainable and secure.

##### Fantastic documentation.

We'd like to think so, at least!

##### 1:1 or greater code to comment ratio.

Code should be self-descriptive and obvious.

##### Extensive road map.

Changes to the library demand meditation to ensure feature creep and organic growth are kept in check.

## Code Metrics

| `marrow.mongo` as of `a889491` | Value |
| --- | --- |
| **Total Lines** | 2,976 |
| **SLoC** | 1,479 |
| **Logical Lines** | 840 |
| **Functions** | 57 |
| **Classes** | 41 |
| **Modules** | 23 |
| **Average Complexity** | 2.460 |
| **Complexity 95th %** | 6 |
| **Maximum Complexity** | 17 |
| **# > 15 Complexity** | 1 |
| **Bytecode Size** | 71 KiB |

{% endmethod %}

Additionally, it provides a very light-weight database connection plugin for the [WebCore web framework](https://github.com/marrow/WebCore) and Python standard logging adapter to emit logs to MongoDB.

This is a living document, evolving as the framework evolves.  You can always browse any point in time within the source repository to review previous versions of these instructions.

{% method -%}

{% common -%}

{% endmethod %}
