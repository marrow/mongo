# Marrow Mongo **Guide**

## Introduction

Documents are the records of [MongoDB](https://www.mongodb.com/), stored in an efficient binary form called [BSON](http://bsonspec.org/), allowing record manipulation that is cosmetically similar to [JSON](http://json.org/). In Python these are typically represented as [dictionaries](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict), Python's native mapping type. Marrow Mongo provides a [`Document`](../api/document.md) mapping type that is directly compatible with and substitutable anywhere PyMongo uses dictionaries.

This package utilizes the [Marrow Schema](https://github.com/marrow/schema#readme) declarative schema toolkit and extends it to encompass MongoDB data storage concerns. Its documentation may assist you in understanding the processes involved in Marrow Mongo. At a fundamental level you define data models by importing classes describing the various components of a collection, such as ``Document``, ``ObjectId``, or ``String``, then compose them into a declarative class model whose attributes describe the data structure, constraints, etc.

`Field` types and `Document` mix-in classes (_traits_) meant for general use are registered using Python standard [_entry points_](http://setuptools.readthedocs.io/en/latest/setuptools.html#extensible-applications-and-frameworks) and are directly importable from the `marrow.mongo.field` and `marrow.mongo.trait` package namespaces respectively.

Within this guide fields are broadly organized into three categories:

* **Simple fields** are fields that hold _scalar values_, variables that can only hold one value at a time. This covers most datatypes you use without thinking: strings, integers, floating point or decimal values, etc.

* **Complex fields** cover most of what's left: variables that can contain multiple values. This includes arrays (`list` in Python, `Array` in JavaScript), compound mappings (_embedded documents_), etc.

* **Complicated fields** are represented by fields with substantial additional logic associated with them, typically through complex typecasting, or by including wrapping objects containing additional functionality. These are separate as they represent substantial additions to core MongoDB capabilities, possibly with additional external dependencies.


## Document Modelling

The `Document` class heirarchy is organized to structure both data and the code manipulating it into clearly defined problems, with composable components focused on the principle of least concern. As such, the base class assumes very little; by itself it is a [`MutableMapping`](https://docs.python.org/3/library/collections.abc.html?highlight=abc#collections.abc.MutableMapping) abstract base class-compatible ordered dictionary proxy or wrapper, usable anywhere a mapping is usable. A notable difference is that the constructor only accepts arguments which have discrete fields associated with them.

There is no need for a specialized "dynamic" variant. Similarly, we have the philosophy that all documents are embeddable. Top-level documents in a collection, which expect an identifier, should utilize the specialization—_trait_—`Identified`.

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
The last field we will define is an array of free-form string tags. This is a complex field whose first argument is the type of value it contains and defaults to an empty version of the complex type it represents if assignment is enabled to eliminate the need for boilerplate code.
{% sample lang="python" -%}
```python
	tag = Array(String(), assign=True)
```
{% endmethod %}
{% method -%}
Lastly we define a unique index on the username to speed up any queries involving that field, and to enforce uniqueness. Because MongoDB's index capabilities are quite expressive, we do not define index features on fields themselves. It is generally a good idea to underscore-prefix non-field attributes. This helps keep fields distinct from non-fields in a visual way and implies they are "protected" or "private" as is customary in Python, though not enforced.
{% sample lang="python" -%}
```python
	
	_username = Index('username', unique=True)
```
{% endmethod %}

Now that we have a document defined we can move on to exploring how to interact with them.


## Collection Management

`Document` subclasses utilizing the `Collection` trait (which `Queryable` inherits) gain class-level _active record_ behaviours. Additionally, `Collection` inherits `Identified` as well, providing an automatically generated ObjectId field named `id` which maps to the stored `_id` key. There is a fairly substantial number of [collection metadata and calculated properties](reference/trait/collection.md#metadata) available.




## Document Interaction

With a document schema defined we can now begin populating data:

{% label %}Python REPL{% endlabel %}
```python
alice = Account('amcgregor', "Alice Bevan-McGregor", age=27)
print(alice.id)  # Already has an ID.
print(alice.id.generation_time)  # This even includes the creation time.
```
As can be seen above construction accepts positional and keyword parameters. Fields will be filled, positionally, in the order they were defined, unless otherwise adjusted using the `adjust_attribute_sequence` decorator.

Assuming a `pymongo` collection is accessible by the variable name `collection` we can construct our index:

```python
Account.create_indexes(collection)
```

There is no need to run this command more than once unless the collection is dropped.

Let's insert our record:

```python
result = collection.insert_one(alice)
assert result.acknowledged and result.inserted_id == alice.id
```

Yup, that's it. Instances of `Document` are directly usable in place of a dictionary argument to `pymongo` methods. We then validate that the document we wanted inserted was, in fact, inserted. Using an assertion in this way, this validation will not be run in production code executed with the `-O` option passed (or `PYTHONOPTIMIZE` environment variable set) in the invocation to Python.


## Querying and Management

Given the `Account` model defined in above, a PyMongo collection object, and a record stored in the database we can retrieve it back out and get the result as an ``Account`` instance:

{% method -%}
Several things are going on here. First it's important to note that Marrow Mongo isn't making the query happen for you, and does not automatically cast dictionaries to `Document` subclasses when querying. The first line demonstrates the native approach to building *filter documents*, the first argument to `find` or `find_one`.

{% sample lang="python" -%}
```python
record = collection.find_one(Account.username == 'amcgregor')
record = Account.from_mongo(record)

print(record.name) # Alice Bevan-McGregor
```
{% endmethod %}

You can use standard Python comparison operators, bitwise operators, and several additional querying methods through class-level access to the defined fields. The result of one of these operations or method calls is a dictionary-like object that is the query. They may be combined through bitwise and (`&`) and bitwise or (`|`) operations. Due to Python's order of operations individual field comparisons must be wrapped in parenthesis if combining.

Combining produces a new `Ops` instance; it is possible to use these to pre-construct parts of queries for later use. It can save time (and visual clutter) to assign the document class to a short, single-character variable name to make repeated reference easier.


## Fields

Included with Marrow Mongo are field types covering all core types supported by MongoDB. A class model is used to define new field types, with a large amount of functionality provided by the base `Field` class itself.

{% method -%}
This base class is directly usable where the underlying field type is dynamic or not known prior to access, i.e. "dynamic".

The `Field` class is a subclass of Marrow Schema's `Attribute` and all field instances applicable to a given `Document` class or instance are accessible using the ordered dictionary `__fields__`.

{% sample lang="python" -%}
```python
from marrow.mongo import Document, Field

class Sample(Document):
	name = Field()

assert 'name' in Sample.__fields__
```
{% endmethod %}


### Name Mapping

{% method -%}
In general, basic fields accept one positional parameter: the name of the field to store data against within MongoDB. In the following example any attempt to read or write to the `field` attriute of a `MyDocument` instance will instead retrieve data from the backing document using the key `name`. If no name is specified explicitly the name of the attribute the field is assigned to is used by default.

You can also pass this name using the `name` keyword argument. This is required (if overriding the default name) for complex field types described later.

{% sample lang="python" -%}
```python
from marrow.mongo import Document

class MyDocument(Document):
	field = Field('name')
```
{% endmethod %}


### Default Values

There are a few attributes of a field that determine what happens when an attempt is made to access a value that currently does not exist in the backing document. If no default is provided and there is no value in the backing store for the field, any attempt to read the value of the field through attribute access will result in an `AttributeError` exception.

<dl>
	<dt>
		<h5 id="default-values-assign"><code>assign</code></h5>
	</dt><dd>
		<p>
			If a default value is provided, automatically assign it to the backing document when a new instance is constructed.
		</p>
		<p>
			<label>Default</label><code>False</code>
		</p>
	</dd>
	<dt>
		<h5 id="default-values-default"><code>default</code></h5>
	</dt><dd>
		<p>
			A single value to store, or a function called to generate a new value on first access (the default) or on instance construction (if <code>assign</code> is <code>True</code>).
		</p>
		<p>
			<label>Default</label><em>No default.</em>
		</p>
	</dd>
	<dt>
		<h5 id="default-values-nullable"><code>nullable</code></h5>
	</dt><dd>
		<p>
			If <code>True</code>, will store <code>None</code>.  If <code>False</code>, will store non-<code>None</code> values, or not store. (The key will be missing from the backing store.)
		</p>
		<p>
			<label>Default</label><code>False</code>
		</p>
	</dd>
	<dt>
		<h5 id="default-values-required"><code>required</code></h5>
	</dt><dd>
		<p>
			This field must have a value assigned; <code>None</code> and an empty string are values.
		</p>
		<p>
			<label>Default</label><code>False</code>
		</p>
	</dd>
</dl>


### Limiting Choice

Passing either an iterable of values, or a callback producing an iterable of values, as the `choices` argument allows you to restrict the acceptable values for the field. If static, this list will be included in the validation document. In this way you can emulate an enum or a set if applied to a field encapsulated in an `Array`.

The ability to restrict acceptable values this way is available to all types of field. Some, such as `Number` and its more specific subclasses, provide additional methods to restrict allowable values, such as ranges or minimums and maximums.


### Field Exclusivity

{% method -%}
Occasionally it may be useful to have two distinct fields where it is acceptable to have a value assigned to only one. We model this dependency through exclusion. By passing a `set` of field names as the `exclusive` argument you can define the fields that must not be set for the current field to be assignable.

Similar to this example, if you wish to define mutual exclusivity you must define both sides of the limitation. `MyDocument` declares that if `link` is set, `mail` can not be set, and likewise the reverse.

{% sample lang="python" -%}
```python
class MyDocument(Document):
	link = Field(exclusive={'mail'})
	mail = Field(exclusive={'link'})
```
{% endmethod %}


### Data Transformation

As we rely on Marrow Schema we make use of its transformation and validation APIs (and objects) to allow for customization of both data ingress and egress. By default Marrow Mongo attempts to ensure the value stored behind-the-scenes matches MongoDB and BSON datatype expectations to allow for conversion-free final use.


#### Overriding Transformation

{% method -%}
If one wanted to store Python `Decimal` objects within the database and wasn't running the latest MongoDB version which has direct support for this type, you could store them safely as strings. An easy way to accomplish this is to use Marrow Schema's `Decimal` transformer.

When attempting to retrieve the value, the string stored in the database will be converted to a `Decimal` object automatically.  When assigning a `Decimal` value to the attribute it will be likewise converted back to a string for storage in MongoDB.

{% sample lang="python" -%}
```python
from marrow.schema.transform import decimal

class MyDocument(Document):
	field = Field(transformer=decimal)
```
{% endmethod %}

#### Transformation in Field Subclasses

{% method -%}
There is a shortcut for handling transformation (when using the default transfomer) in field subclasses, used extensively by the built-in field types. When subclassing `Field` you can simply define a `to_native` and/or `to_foreign` method.

These methods are passed the document the field is attached to, the name of the field, and the value being read or written. They must return either the same value, or some value after hypothetical transformation. The reason for the seeming duplication of the field information (which would otherwise be accessible via `self`) is to allow for the assignment of non-method functions, callable objects, or static methods.

{% sample lang="python" -%}
```python
class AwesomeField(Field):
	def to_native(self, doc, name, value):
		return value
	
	def to_foreign(self, doc, name, value):
		return str(value).upper()
```
{% endmethod %}


### Data Validation

{% method -%}
By default no data validation is performed beyond the errors that may be raised during datatype transformation for a given `Field` subclass. Any field-level configuration for validation-like features effect the generation of the MongoDB-side validation document. You can make use of custom client-side valiation within your own models by utilizing Marrow Schema validation objects.

This example provides a username-based `_id` field.

{% sample lang="python" -%}
```python
from marrow.schema.validate.pattern import username

class MyDocument(Document):
	id = Field('_id', validator=username)
```
{% endmethod %}


### Predicates

There are several predicates that apply to all fields. These are callbacks, callable objects, or evaluated as ACL trinary booleans (`is None` vs. `bool()`) if not otherwise callable, allowing for simple "always" and "never" static values.


#### Projection

{% method -%}
Subclasses of `Document` provide a `__projection__` attribute containing the default set of fields to project based on field `project` predicates. Behaviour is somewhat complex; all fields excluding those marked for exclusion (`False`) are projected unless any are marked for explicit inclusion (`True`) in which case just those are. Fields whose predicates evaluate to `None` (the default) will only be included in the former case.

{% sample lang="python" -%}
```python
class MyDocument(Document):
	foo = Field()
	bar = Field(project=None)
	baz = Field(project=False)

MyDocument.__projection__ == {'foo': True, 'bar': True}
```
{% endmethod %}


#### Read/Write Permissions

{% method -%}
The shortcut methods `is_readable(context=None)` and `is_writeable(context=None)` are provided to evaluate the `read` and `write` predicates, which follow a pattern similar to projection. Literal `True` and `False` are allowed as constants to represent "always" and "never". These may alternatively be callbacks (or callable objects) which optionally take a context argument and return `True` or `False`, or an iterable of such objects which may also return `None` to abstain from voting in the access control list (ACL).

{% sample lang="python" -%}
```python
class MyDocument(Document):
	foo = Field(write=False)

MyDocument.foo.is_writeable() == False
```
{% endmethod %}


#### Sorting

Virtually identical to the read and write access permissions, the `sort` predicate follows the same rules and provides an `is_sortable(context=None)` evaluation method.






## Indexes


## Trait Mix-Ins



## Plugin Namespaces
