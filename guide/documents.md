# Defining Documents

Documents are the records of MongoDB, stored in an efficient binary form called [BSON](http://bsonspec.org) allowing record manipulation that is cosmetically similar to JSON. In Python these are typically represented as dictionaries, Python's native mapping type. Marrow Mongo provides a `Document` mapping type that is directly compatible with and substitutable anywhere PyMongo uses dictionaries.

{% method -%}
This package utilizes the [Marrow Schema](https://github.com/marrow/schema#readme) declarative schema toolkit and extends it to encompass MongoDB data storage concerns. Its documentation may assist you in understanding the processes involved in Marrow Mongo. At a fundamental level you define data models by importing classes describing the various components of a collection, such as ``Document``, ``ObjectId``, or ``String``, then compose them into a declarative class model whose attributes describe the data structure, constraints, etc.

Begin by importing various components from the `marrow.mongo` package.

{% sample lang="python" -%}
```python
from marrow.mongo import Index
from marrow.mongo.field import ObjectId, String, Number, Array
from marrow.mongo.trait import Identified
```
{% endmethod %}

`Field` types and `Document` mix-in classes (_traits_) meant for general use are registered using Python standard [_entry points_](http://setuptools.readthedocs.io/en/latest/setuptools.html#extensible-applications-and-frameworks) and are directly importable from the `marrow.mongo.field` and `marrow.mongo.trait` package namespaces respectively.

Within this guide fields are broadly organized into three categories:

* **Simple fields** are fields that hold _scalar values_, variables that can only hold one value at a time. This covers most datatypes you use without thinking: strings, integers, floating point or decimal values, etc.

* **Complex fields** cover most of what's left: variables that can contain multiple values. This includes arrays (`list` in Python, `Array` in JavaScript), compound mappings (_embedded documents_), etc.

* **Complicated fields** are represented by fields with substantial additional logic associated with them, typically through complex typecasting, or by including wrapping objects containing additional functionality. These are separate as they represent substantial additions to core MongoDB capabilities, possibly with additional external dependencies.

The `Document` class heirarchy is organized to structure both data and the code manipulating it into clearly defined problems, with composable components focused on the principle of least concern. As such, the base class assumes very little; by itself it is a `MutableMapping` abstract base class-compatible ordered dictionary proxy or wrapper, usable anywhere a mapping is usable.

There is no need for a specialized "dynamic" variant. Similarly, we have the philosophy that all documents are embeddable. Top-level documents in a collection, which expect an identifier, utilize the specialization—_trait_—`Identified`. The majority of _active record_ behaviour is itself also a trait, `Queryable`.

{% method -%}
To define a schema, create a `Document` subclass. In this example one to store information about user accounts. Populate it with a few different types of field by assigning `Field` instances as class attributes.

Additional metadata is stored against double-underscore "magic" attributes, such as `__collection__` to identify the in-database collection name to utilize. It is generally a good idea to underscore-prefix non-field attributes. This helps keep fields distinct from non-fields in a visual way and implies they are "protected" or "private" as is customary in Python, though not enforced.

{% sample lang="python" -%}
```python
class Account(Collection):
	__collection__ = 'accounts'
	__validate__ = 'strict'
	
	name = String()
	username = String(required=True)
	locale = String(default='en-CA', assign=True)
	age = Number(default=None)
	tag = Array(String(), assign=True)
	
	_username = Index('username', unique=True)
```
{% endmethod %}


```python
class Account(Collection):
```

We subclass `Collection`, which itself is a child class of `Identified` (these documents have an `id` field mapping to `_id` in MongoDB), and `Document`. All documents and traits you define must ultimately subclass `Document` in order to utilize the metaclass that makes the declarative mechanisms operate.

```python
__collection__ = 'accounts'
__validate__ = 'strict'
```

These are metadata attributes. The first is defined and optionally utilized by the `Collection` trait to identify which database collection to utilize. If you do not define this attribute you must pass a collection, not a database, to `Collection` methods.

```python
name = String()
```

The first field defined is a simple string, with no constraints or transformation options given. Because no default value was given, any attempt to retrieve this attribute on an instance of `Account` prior to assigning one will raise an `AttributeError`, as a value for the field would not exist at all.

```python
username = String(required=True)
```

Fields missing from the document might be A-OK in some circumstances, but not all. We can mark `username` as required, resulting in the addition of a constraint when generating the validation document for accounts.

```python
locale = String(default='en-CA-u-tz-cator-cu-CAD', assign=True)
```

When utilizing default values you may choose to have the default value written immediately into the document, unless overridden. By utilizing the `assign` option the default value will be assigned to the instance immediately upon instantiation, resulting in the default value being present in the database. This armors records against potential future changes in the default value, if you do not wish such changes to propagate.

```python
age = Number()
```

This allows storage of any numeric value, either integer or floating point. Now there is the record identifier:

```python
id = ObjectId('_id', assign=True)
```

Marrow Mongo does not assume your documents contain IDs; there is no separation at the top level between documents for storage within a collection and _embedded documents_, leaving the declaration of an ID up to you. You might not always wish to use an ObjectID, either; please see MongoDB's documentation for discussion of general modelling practices. The first positional parameter for most non-complex fields is the name of the MongoDB-side field. Underscores imply an attribute is _protected_ in Python, so we remap it by assigning it to just `id`. The `assign` argument here ensures whenever a new `Account` is instantiated an ObjectID will be immediately generated and assigned.

Finally there is an array of tags:

```python
tag = Array(String(), assign=True)
```

This combines what we've been using so far into one field. An `Array` is a *complex field* (a container) and as such the types of values allowed to be contained therein may be defined positionally. If you want to override the field's database-side name, pass in a `name` as a keyword argument. As we tell Marrow Mongo to `assign` the defualt value, a new array (`list` in Python) will be constructed and assigned with each new instance, ensuring we always have a place to put additional data.

Lastly we define a unique index on the username to speed up any queries involving that field:

```python
_username = Index('username', unique=True)
```
