# Boolean

{% method -%}
Boolean fields store boolean values, as expected.  It also provides convienence for accepting _truthy_ or _falsy_ values. See the usage section for more details.

<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo.field import Boolean</code></p></dd>
	<dt><h5>Inherits</h5></dt><dd><p><code>marrow.mongo:<strong>Field</strong></code></p></dd>
</dl>

{%common -%}

#### Contents

1. [Attributes](#attributes)
2. [Usage](#usage)
3. [Examples](#examples)

{% endmethod %}


## Attributes

This field type inherits all [`Field` attributes](field.md#attributes) and represents a singular, scalar boolean
value.  In addition to the storage and retrieval of pure `True` and `False` values, the field configuration defines allowable "truthy" values (to cast to `True`) and "falsy" values (to cast to `False`).

<dl>
	<dt><h5><code>truthy</code></h5></dt><dd>
		<p>Values to interpret as <code>True</code>, storing <code>True</code> if they are assigned.</p>
		<p><label>Default</label><code>('true', 't', 'yes', 'y', 'on', '1', True)</code></p>
		<p><label>Added</label><code>&gt;=1.1.3</code></p>
	</dd><dt><h5><code>falsy</code></h5></dt><dd>
		<p>Values to interpret as <code>False</code>, storing <code>False</code> if they are assigned.</p>
		<p><label>Default</label><code>('false', 'f', 'no', 'n', 'off', '0', False)</code></p>
		<p><label>Added</label><code>&gt;=1.1.3</code></p>
	</dd>
</dl>

In versions prior to 1.1.3 the "truthy" and "falsy" values are hardcoded at the defaults presented above.


## Usage

Instantiate and assign an instance of this class during construction of a new `Document` subclass. Accessing as a class attribute will return a Queryable allowing filtering operations, and access as an instance attribute will return a `bool` cast value.

Assignment of any value matched by the `truthy` iterable (via `in` comparison) will store `True`, and likewise with the `falsy` iterable storing `False`. Additionally, if an attempt is made to assign a non-boolean, non-string value, the value will be passed through `bool()` conversion prior to storage, allowing use of objects which define their own `__nonzero__`/`__bool__` methods.

