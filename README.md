---
description: An introduction to the Marrow Mongo Document Mapper and overview of features.
---
# The Marrow Mongo Document Mapper

Marrow Mongo is a collection of small, focused utilities written to enhance use of the [PyMongo native MongoDB driver](http://api.mongodb.com/python/current/) without the overhead, glacial update cycle, complexity, and head-space requirements of a full *active record* object document mapper.

{% method -%}
## Overview

[![version](http://img.shields.io/pypi/v/marrow.mongo.svg?style=flat "Latest version.")](https://pypi.python.org/pypi/marrow.mongo) 
[![tag](https://img.shields.io/github/tag/marrow/mongo.svg "Latest tag.")](https://github.com/marrow/mongo/releases/latest) 
[![watch](https://img.shields.io/github/watchers/marrow/mongo.svg?style=social&label=Watch "Subscribe to project activity on Github.")](https://github.com/marrow/mongo/subscription)
[![star](https://img.shields.io/github/stars/marrow/mongo.svg?style=social&label=Star "Star this project on Github.")](https://github.com/marrow/mongo/subscription)
[![fork](https://img.shields.io/github/forks/marrow/mongo.svg?style=social&label=Fork "Fork this project on Github.")](https://github.com/marrow/mongo/fork)

##### Declarative document modeling.

Instantiate field objects and associate them with custom `Document` sub-classes to model your data declaratively.

```python
class Television(Document):
	model = String()
```

##### Refined, Pythonic _data access object_ interactions.

Utilize `Document` instances as attribute access mutable mappings with value typecasting, directly usable with PyMongo APIs. Attention is paid to matching Python language expectations, such as allowing instantiation using positional arguments. Values are always stored in the PyMongo-preferred MongoDB native format, and cast on attribute access as needed.

```python
tv = Television('D50u-D1')
assert tv.model == 'D50u-D1'
collection.insert_one(tv)
```

##### Collection and index metadata, and creation shortcuts.

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

[![status](http://img.shields.io/travis/marrow/mongo/master.svg?style=flat "Release build status.")](https://travis-ci.org/marrow/mongo/branches) 
[![coverage](http://img.shields.io/codecov/c/github/marrow/mongo/master.svg?style=flat "Release test coverage.")](https://codecov.io/github/marrow/mongo?branch=master) 
[![health](https://landscape.io/github/marrow/mongo/master/landscape.svg?style=flat "Release code health.")](https://landscape.io/github/marrow/mongo/master) 
[![dependencies](https://img.shields.io/requires/github/marrow/mongo.svg "Status of release dependencies.")](https://requires.io/github/marrow/mongo/requirements/?branch=master)

##### Guaranteed to be fully tested before any release.

We utilize [Travis](https://travis-ci.org/marrow/mongo/) continuous integration, with test coverage reporting provided by [Codecov.io](https://codecov.io/gh/marrow/mongo/). We also monitor requirements for security concerns and deprecation using [Requires.io](https://requires.io/github/marrow/mongo/requirements/?branch=master). Extensive static analysis through [Landscape.io](https://landscape.io/marrow/mongo/) and proactive use of tools such as [pre-commit](http://pre-commit.com), with [plugins](https://github.com/marrow/mongo/blob/develop/.pre-commit-config.yaml) such as the infosec analyzer [OpenStack Bandit](https://wiki.openstack.org/wiki/Security/Projects/Bandit), plus various linting tools, help to keep code maintainable and secure.

##### Extensively documented, with a > 1:1 code to comment ratio.

Every developer has run into those objects that fail to produce sensible or useful programmers' representation, generate meaningless exception messages, or fail to provide introspective help. With more documentation in the code than code, you won't find that problem here. Code should be self-descriptive and obvious; we feel comments and _docstrings_ are integral to this.

##### A considered road map.

Changes to the library demand [meditation](https://github.com/marrow/mongo/projects) to ensure feature creep and organic growth are kept in check. Where possible, solutions involving objects passed to standard PyMongo functions and methods are preferred to solutions involving wrapping, proxying, or middleware. All but minor changes are isolated in [pull requests](https://github.com/marrow/mongo/pulls) to aid in code review.

## MIT Licensed

The [MIT License](license.md) is highly permissive, allowing **commercial** and **non-commercial** _use_, _reproduction_, _modification_, _republication_, _redistribtution_, _sublicensing_, and _sale_ of the software (and associated documentation) and its components. This, given that the license notice is included in the reproduced work, and that any warranty or liability on behalf of the [Marrow Open Source Collective](https://github.com/marrow/) or [project contributors](https://github.com/marrow/mongo/graphs/contributors) is waived.

You are effectively free to deal in this software however you choose, **without commercial hinderance**, unlike some other open-source licenses.

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
