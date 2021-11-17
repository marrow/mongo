# Fields

Included with Marrow Mongo are field types covering all core types supported by MongoDB. A class model is used to define new field types, with a large amount of functionality provided by the base `Field` class itself.

This base class is directly usable where the underlying field type is dynamic or not known prior to access.

The `Field` class is a subclass of Marrow Schema's `Attribute` and all field instances applicable to a given `Document` class or instance are accessible using the ordered dictionary `__fields__`.

```python
from marrow.mongo import Document, Field

class Sample(Document):
    name = Field()

assert 'name' in Sample.__fields__
```

## Name Mapping

In general, basic fields accept one positional parameter: the name of the field to store data against within MongoDB. In the following example any attempt to read or write to the `field` attriute of a `MyDocument` instance will instead retrieve data from the backing document using the key `name`. If no name is specified explicitly the name of the attribute the field is assigned to is used by default. The most frequent use of this is in mapping the `_id` field from MongoDB to a less cumbersome property name.

You can also pass this name using the `name` keyword argument. This may be required (if overriding the default name) for non-basic field types, and is required for complex types.

```python
from marrow.mongo import Document

class MyDocument(Document):
    field = Field('name')
```

## Defaults & Values

There are a few attributes of a field that determine what happens when an attempt is made to access a value that currently does not exist in the backing document. If no default is provided and there is no value in the backing store for the field, any attempt to read the value of the field through attribute access will result in an `AttributeError` exception.

You are additionally given control over what happens when the default value is assigned to the field or the value is deleted (via `del`) from the document.

### `assign` <a href="default-values-assign" id="default-values-assign"></a>

&#x20;If a default value is provided, automatically assign it to the backing document when a new instance is constructed.

&#x20;Default`False`

### `default` <a href="default-values-default" id="default-values-default"></a>

&#x20;A single value to store, or a function called to generate a new value on first access (the default) or on instance construction (if `assign` is `True`).

&#x20;Default_No default._

### `nullable` <a href="default-values-nullable" id="default-values-nullable"></a>

&#x20;If `True`, will store `None`. If `False`, will store non-`None` values, or not store. (The key will be missing from the backing store.)

&#x20;Default`False`

### `required` <a href="default-values-required" id="default-values-required"></a>

&#x20;This field must have a value assigned; `None` and an empty string are values.

&#x20;Default`False`

## Limiting Choice

### `choices`

Passing either an iterable of values, or a callback producing an iterable of values, as the `choices` argument allows you to restrict the acceptable values for the field. If static, this list will be included in the validation document. In this way you can emulate an enum or a set if applied to a field encapsulated in an `Array`.

The ability to restrict acceptable values this way is available to all types of field. Some, such as `Number` and its more specific subclasses, provide additional methods to restrict allowable values, such as ranges or minimums and maximums.

## Field Exclusivity

### `exclusive`

Occasionally it may be useful to have two distinct fields where it is acceptable to have a value assigned to only one. We model this dependency through exclusion. By passing a `set` of field names as the `exclusive` argument you can define the fields that must not be set for the current field to be assignable.

Similar to this example, if you wish to define mutual exclusivity you must define both sides of the limitation. `MyDocument` declares that if `link` is set, `mail` can not be set, and likewise the reverse.

```python
class MyDocument(Document):
    link = Field(exclusive={'mail'})
    mail = Field(exclusive={'link'})
```

## Data Transformation

### `transformer`

As we rely on Marrow Schema we make use of its transformation and validation APIs (and objects) to allow for customization of both data ingress and egress. By default Marrow Mongo attempts to ensure the value stored behind-the-scenes matches MongoDB and BSON datatype expectations to allow for conversion-free final use.

If one wanted to store Python `Decimal` objects within the database and wasn't running the latest MongoDB version which has direct support for this type, you could store them safely as strings. An easy way to accomplish this is to use Marrow Schema's `Decimal` transformer.

When attempting to retrieve the value, the string stored in the database will be converted to a `Decimal` object automatically. When assigning a `Decimal` value to the attribute it will be likewise converted back to a string for storage in MongoDB.

```python
from marrow.schema.transform import decimal

class MyDocument(Document):
    field = Field(transformer=decimal)
```

### Transformation in Field Subclasses

There is a shortcut for handling transformation (when using the default transfomer) in field subclasses, used extensively by the built-in field types. When subclassing `Field` you can simply define a `to_native` and/or `to_foreign` method.

These methods are passed the document the field is attached to, the name of the field, and the value being read or written. They must return either the same value, or some value after hypothetical transformation. The reason for the seeming duplication of the field information (which would otherwise be accessible via `self`) is to allow for the assignment of non-method functions, callable objects, or static methods.

```python
class AwesomeField(Field):
    def to_native(self, doc, name, value):
        return value

    def to_foreign(self, doc, name, value):
        return str(value).upper()
```

## Data Validation

### `validator`

By default no data validation is performed beyond the errors that may be raised during datatype transformation for a given `Field` subclass. Any field-level configuration for validation-like features effect the generation of the MongoDB-side validation document. You can make use of custom client-side valiation within your own models by utilizing Marrow Schema validation objects.

This example provides a username-based `_id` field.

```python
from marrow.schema.validate.pattern import username

class MyDocument(Document):
    id = Field('_id', validator=username)
```

## Projection

### `project`

Subclasses of `Document` provide a `__projection__` attribute containing the default set of fields to project based on field `project` predicates. Behaviour is somewhat complex; all fields excluding those marked for exclusion (`False`) are projected unless any are marked for explicit inclusion (`True`) in which case just those are. Fields whose predicates evaluate to `None` (the default) will only be included in the former case.

```python
class MyDocument(Document):
    foo = Field()
    bar = Field(project=None)
    baz = Field(project=False)

MyDocument.__projection__ == {'foo': True, 'bar': True}
```

## Read/Write Permissions

### `read` & `write`

The shortcut methods `is_readable(context=None)` and `is_writeable(context=None)` are provided to evaluate the `read` and `write` predicates, which follow a pattern similar to projection. Literal `True` and `False` are allowed as constants to represent "always" and "never". These may alternatively be callbacks (or _callable objects_) which optionally take a context argument and return `True` or `False`, or an iterable of such objects which may also return `None` to abstain from voting in the access control list (ACL).

```python
class MyDocument(Document):
    foo = Field(write=False)

MyDocument.foo.is_writeable() == False
```

## Sorting

### `sort`

Virtually identical to the `read` and `write` access permissions, the `sort` predicate follows the same rules and provides an `is_sortable(context=None)` evaluation method.
