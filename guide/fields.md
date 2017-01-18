# Fields

Included with Marrow Mongo are field types covering all core types supported by MongoDB. A class model is used to define new field types, with a large amount of functionality provided by the base `Field` class itself. This base class is directly usable where the underlying field type is dynamic or not known prior to access.

The `Field` class is a subclass of Marrow Schema's `Attribute` and all field instances applicable to a given `Document` class or instnace are accessible using the ordered dictionary `__fields__`.

## Field

```python
from marrow.mongo import Field
```


### Name Mapping

{% method -%}
In general, basic fields accept one positional parameter: the name of the field to store data against within MongoDB. In the following example any attempt to read or write to the `field` attriute of a `MyDocument` instance will instead retrieve data from the backing document using the key `name`. If no name is specified explicitly the name of the attribute the field is assigned to is used by default.

You can also pass this name using the keyword argument `name`; this is required (if overriding the default name) for complex field types described later.

{% sample lang="python" -%}
```python
class MyDocument(Document):
	field = Field('name')
```
{% endmethod %}


### Default Values

{% method -%}
There are a few attributes of a field that determine what happens when an attempt is made to access a value that currently does not exist in the backing document. If no default is provided and there is no value in the backing store for the field any attempt to read the value of the field through attribute access will result in an `AttributeError` exception.

{% sample lang="python" -%}
* **`assign`**

  If a default value is provided, automatically assign it to the backing document when a new instance is constructed.

* **`default`**

  A single value to store, or a function called to generate a new value on first access (the default) or on instance construction (if `assign` is `True`).

* **`nullable`**

  If `True`, will store `None`.  If `False`, will store non-`None` values, or not store.

* **`required`**

  This field must have a value assigned; `None` and an empty string are values.
{% endmethod %}


### Limiting Choice

Passing an iterable of values or a callback producing an iterable of values as the `choices` argument allows you to restrict the acceptable values for the field. If static, this list will be included in the validation document. In this way you can emulate an enum or a set if applied to a field encapsulated in an `Array`.

The ability to restrict acceptable values this way is available to all types of field. Some, such as `Number` and its more specific subclasses, provide additional methods to restrict allowable values, such as ranges or minimums and maximums.


## Field Exclusivity

{% method -%}
Occasionally it may be useful to have two distinct fields where it is acceptable to have a value assigned to only one. We model this dependency through exclusion. By passing a (literal) set of field names as the `exclusive` argument you can define the fields that must not be set for the current field to be assignable.

Similar to this example, if you wish to define mutual exclusivity you must define both sides of the limitation. Here, `MyDocument` declares that if `link` is set `mail` can not be set, and likewise the reverse.

{% sample lang="python" -%}
```python
class MyDocument(Document):
	link = String(exclusive={'mail'})
	mail = String(exclusive={'link'})
```
{% endmethod %}


## Transformation and Validation

As we rely on Marrow Schema we make use of its transformation and validation APIs (and objects) to allow for customization of both data ingress and egress. By default Marrow Mongo attempts to ensure the value stored behind-the-scenes matches MongoDB and BSON datatype expectations to allow for conversion-free final use.


### Overriding Transformation

{% method -%}
If one wanted to store Python `Decimal` objects within the database and wasn't running the latest MongoDB version which has direct support for this type, you could store them safely as strings. An easy way to accomplish this is to use Marrow Schema's `Decimal` transformer.

When attempting to retrieve the value the string stored in the database will be converted to a `Decimal` object automatically.  When assigning a `Decimal` value to the attribute it will be likewise converted back to a string for storage in MongoDB.

{% sample lang="python" -%}
```python
from marrow.mongo import Document
from marrow.mongo.field import String
from marrow.schema.transform import decimal

class MyDocument(Document):
	field = String(transformer=decimal)
```
{% endmethod %}

{% method -%}
Additionally there is a shortcut for handling validation (when using the default validator) in field subclasses, used extensively by the built-in field types. When subclassing `Field` you can simply define a `to_native` and/or `to_foreign` method.

These methods are passed the document the field is attached to, the name of the field, and the value being read or written. They must return either the same value, or some value after hypothetical transformation. The reason for the seeming duplication of the field information (which would otherwise be accessible via `self`) is to allow for the assignment of non-method functions, callable objects, or static methods.

{% sample lang="python" -%}
```python
from marrow.mongo import Field

class AwesomeField(Field):
	def to_native(self, doc, name, value):
		return value
	
	def to_foreign(self, doc, name, value):
		return str(value).upper()
```
{% endmethod %}

