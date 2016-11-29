---
description: An introduction to the Marrow Mongo Document Mapper and overview of features.
---
# The Marrow Mongo Document Mapper

Marrow Mongo is a collection of small, focused utilities written to enhance use of the [PyMongo native MongoDB driver](http://api.mongodb.com/python/current/) without the overhead, glacial update cycle, complexity, and head-space requirements of a full *active record* object document mapper. This project grew out of the need (both personal, and commercial) to find a viable, simple, well-tested alternative to an existing ODM that had begun failing under its own weight. We believe that Marrow Mongo hits the Goldilocks zone for a supportive MongoDB experience in Python, without getting in the way, offering elegant and Pythonic approaches to document storage modelling, access, and interaction.

This is a living document, evolving as the framework evolves.  You can always [browse any point in time](https://github.com/marrow/mongo/commits/book) within the [source repository](https://github.com/marrow/mongo/tree/book) to review previous versions of these instructions. (Try using the "edit this page" link in the upper right if viewing this document on the [official site](https://mongo.webcore.io/).)


{% method -%}
## Overview

[![version](https://img.shields.io/pypi/v/marrow.mongo.svg?style=flat "Latest version.")](https://pypi.python.org/pypi/marrow.mongo) 
[![tag](https://img.shields.io/github/tag/marrow/mongo.svg "Latest tag.")](https://github.com/marrow/mongo/releases/latest) 
[![watch](https://img.shields.io/github/watchers/marrow/mongo.svg?style=social&label=Watch "Subscribe to project activity on Github.")](https://github.com/marrow/mongo/subscription)
[![star](https://img.shields.io/github/stars/marrow/mongo.svg?style=social&label=Star "Star this project on Github.")](https://github.com/marrow/mongo/subscription)
[![fork](https://img.shields.io/github/forks/marrow/mongo.svg?style=social&label=Fork "Fork this project on Github.")](https://github.com/marrow/mongo/fork)

##### Declarative document modeling.

Instantiate field objects and associate them with custom `Document` sub-classes to model your data declaratively.

[Learn more about constructing documents.](guide/documents.md)

```python
class Television(Document):
	model = String()
```

##### Refined, Pythonic _data access object_ interactions.

Utilize `Document` instances as attribute access mutable mappings with value typecasting, directly usable with PyMongo APIs. Attention is paid to matching Python language expectations, such as allowing instantiation using positional arguments. Values are always stored in the PyMongo-preferred MongoDB native format, and cast on attribute access as needed. [Learn more about interacting with documents.](guide/instances.md)

```python
tv = Television('D50u-D1')
assert tv.model == tv['model'] == 'D50u-D1'
```

##### Collection and index metadata, and creation shortcuts.

Keep information about your data model with your data model and standardize access.

[Learn more about indexing.](guide/indexes.md)

```python
class Television(Document):
	__collection__ = 'tv'
	model = String()
	brand = String()
	_model = Index('model')

collection = Television.create_collection(database)
collection.insert_one(Television('D50u-D1'))
```

##### Filter construction through rich comparisons.

Construct filter documents through comparison of (or method calls on) field instances accessed as class attributes.

[Learn more about querying documents.](guide/querying.md)

```python
tv_a = Television.from_mongo(collection.find_one(Television.model == 'D50u-D1'))
tv_b = Television.from_mongo(collection.find_one(Television.model.re(r'^D50\w')))
assert tv_a.model == tv_b.model == 'D50u-D1'
assert tv_a['_id'] == tv_b['_id']
```

##### Parametric filter, projection, sort, and update document construction.

Many Python _active record_ object relational mappers (ORMs) and object document mappers (ODMs) provide a short-hand involving the transformation of named parameters into database concepts.

[Learn more about the parametric helpers.](guide/parametric.md)

```python
collection.update_one(
	F(Television, model__ne='XY-zzy'),
	U(Television, set__brand='Vizio'))

tv = Television.from_mongo(collection.find_one(
		F(Television, model='D50u-D1'),
		P(Television, 'brand')
	))

assert tv.brand == 'Vizio'
```

##### Advanced GeoJSON support.

Marrow Mongo comes with [GeoJSON](http://geojson.org) "batteries included", having extensive support for querying, constructing, and manipulating GeoJSON data.

[Learn more about working with geospatial data.](guide/geospatial.md)

```python
position = Point(longitude, latitude)
collection.find(Battleship.location.near(position))
```

{% common -%}
## Code Quality

[![status](https://img.shields.io/travis/marrow/mongo/master.svg?style=flat "Release build status.")](https://travis-ci.org/marrow/mongo/branches) 
[![coverage](https://img.shields.io/codecov/c/github/marrow/mongo/master.svg?style=flat "Release test coverage.")](https://codecov.io/github/marrow/mongo?branch=master) 
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
