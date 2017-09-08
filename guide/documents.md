# Defining Documents

Documents are the records of [MongoDB](https://www.mongodb.com/), stored in an efficient binary form called [BSON](http://bsonspec.org/), allowing record manipulation that is cosmetically similar to [JSON](http://json.org/). In Python these are typically represented as [dictionaries](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict), Python's native mapping type. Marrow Mongo provides a [`Document`](../api/document.md) mapping type that is directly compatible with and substitutable anywhere PyMongo uses dictionaries.

This package utilizes the [Marrow Schema](https://github.com/marrow/schema#readme) declarative schema toolkit and extends it to encompass MongoDB data storage concerns. Its documentation may assist you in understanding the processes involved in Marrow Mongo. At a fundamental level you define data models by importing classes describing the various components of a collection, such as ``Document``, ``ObjectId``, or ``String``, then compose them into a declarative class model whose attributes describe the data structure, constraints, etc.

`Field` types and `Document` mix-in classes (_traits_) meant for general use are registered using Python standard [_entry points_](http://setuptools.readthedocs.io/en/latest/setuptools.html#extensible-applications-and-frameworks) and are directly importable from the `marrow.mongo.field` and `marrow.mongo.trait` package namespaces respectively.

Within this guide fields are broadly organized into three categories:

* **Simple fields** are fields that hold _scalar values_, variables that can only hold one value at a time. This covers most datatypes you use without thinking: strings, integers, floating point or decimal values, etc.

* **Complex fields** cover most of what's left: variables that can contain multiple values. This includes arrays (`list` in Python, `Array` in JavaScript), compound mappings (_embedded documents_), etc.

* **Complicated fields** are represented by fields with substantial additional logic associated with them, typically through complex typecasting, or by including wrapping objects containing additional functionality. These are separate as they represent substantial additions to core MongoDB capabilities, possibly with additional external dependencies.

The `Document` class heirarchy is organized to structure both data and the code manipulating it into clearly defined problems, with composable components focused on the principle of least concern. As such, the base class assumes very little; by itself it is a [`MutableMapping`](https://docs.python.org/3/library/collections.abc.html?highlight=abc#collections.abc.MutableMapping) abstract base class-compatible ordered dictionary proxy or wrapper, usable anywhere a mapping is usable.

There is no need for a specialized "dynamic" variant. Similarly, we have the philosophy that all documents are embeddable. Top-level documents in a collection, which expect an identifier, utilize the specialization—_trait_—`Identified`. 

{% method -%}
Begin by importing various components from the `marrow.mongo` package or one of the namespace packages for fields and traits, respectively.

{% sample lang="python" -%}
```python
from marrow.mongo import Index
from marrow.mongo.field import ObjectId, String, Number, Array
from marrow.mongo.trait import Queryable
```
{% endmethod %}
{% method -%}
To define a schema construct a `Document` subclass.  In this example, one to store information about user accounts. We utilize the `Queryable` subclass of `Document`, containing the majority of stateless _active record_ behaviour and provide (via `Identified`) an `id` field. All documents and traits you define must ultimately subclass `Document` in order to utilize the metaclass that makes the declarative mechanisms operate.

{% sample lang="python" -%}
```python
class Account(Queryable):
```
{% endmethod %}
{% method -%}
Initially we populate metadata. The first defines the name of the collection to use when _binding_ the class to a database, and is optional; you can bind it to a class directly if you wish, or use it without binding at all. The second states that if the classmethod `create_collection()` is used to specify a default validation level and generate a validation document (schema and/or constraints).
{% sample lang="python" -%}
```python
	__collection__ = 'accounts'
	__validate__ = 'strict'
	
```
{% endmethod %}
{% method -%}
Populate it with a few different types of field by assigning `Field` instances as class attributes. Most accounts represent people, who have names. A simple string, with no constraints or transformation options given. Because no default value was given, any attempt to retrieve this attribute on an instance of `Account` prior to assigning one will raise an `AttributeError`, as a value for the field would not exist at all.
{% sample lang="python" -%}
```python
	name = String()
```
{% endmethod %}
{% method -%}
Fields missing from the document might be A-OK in some circumstances, but not all. We can mark our acount's `username` as required, resulting in the addition of a constraint when generating the validation document.
{% sample lang="python" -%}
```python
	username = String(required=True)
```
{% endmethod %}
{% method -%}
When utilizing default values you may choose to have the default value written immediately into the document. By utilizing the `assign` option the default value will be assigned to the instance immediately upon instantiation, unless passed to the constructor, resulting in the default value being present in the database. This armors records against potential future changes in the default value, if you do not wish such changes to propagate.
{% sample lang="python" -%}
```python
	locale = String(default='en-CA', assign=True)
```
{% endmethod %}
{% method -%}
We technically allow storage of any numeric value, either integer or floating point, for our user's age. To prevent explosions if an age is not given we define a default, though this default will not waste storage space in the database by being assigned.
{% sample lang="python" -%}
```python
	age = Number(default=None)
```
{% endmethod %}
{% method -%}
Finally there is an array of free-form string tags. This is a complex field whose first argument is the type of value it contains and defaults to an empty version of the complex type it represents if assignment is enabled to eliminate the need for boilerplate code.
{% sample lang="python" -%}
```python
	tag = Array(String(), assign=True)
```
{% endmethod %}
{% method -%}
{% sample lang="python" -%}
```python
```
{% endmethod %}
{% method -%}
Lastly we define a unique index on the username to speed up any queries involving that field, and to enforce uniqueness. Because MongoDB's index capabilities are quite expressive, we do not define index features on fields themselves. It is generally a good idea to underscore-prefix non-field attributes. This helps keep fields distinct from non-fields in a visual way and implies they are "protected" or "private" as is customary in Python, though not enforced.
{% sample lang="python" -%}
```python
	
	_username = Index('username', unique=True)
```
{% endmethod %}
{% method -%}
{% sample lang="python" -%}
```python
```
{% endmethod %}

Now that we have a document defined we can move on to [exploring how to interact with them](instances.md).
