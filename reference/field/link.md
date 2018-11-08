# Link

{% method -%}

A Link field type is provided to offer a way to store and retrieve well-formed URI (URL) while optionally restricting the allowable schemes, or protocols.  Internally these values are stored as strings after normalization through the `URI` datatype, and on access provide that URI instance.

<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo.field import Link</code></p></dd>
	<dt><h5>Inherits</h5></dt><dd><p><code>marrow.mongo.field:<strong>String</strong></code></p></dd>
</dl>

{%common -%}

#### Contents

1. [Attributes](#attributes)
2. [Usage](#usage)
3. [Examples](#examples)

{% endmethod %}


## Attributes

This field type inherits all [`Field` attributes](field.md#attributes) and represents a singular, scalar text
value.

## Usage

Instantiate and assign an instance of this class during construction of a new `Document` subclass. Accessing as a class attribute will return a Queryable allowing filtering operations, and access as an instance attribute will return a `URI` cast value.

Assignment of any value matched by the `truthy` iterable (via `in` comparison) will store `True`, and likewise with the `falsy` iterable storing `False`. Additionally, if an attempt is made to assign a non-boolean, non-string value, the value will be passed through `bool()` conversion prior to storage, allowing use of objects which define their own `__nonzero__`/`__bool__` methods.

