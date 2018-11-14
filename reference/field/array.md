# Array

An `Array` is used to contain zero or more other values (representable using fields) in the form of a numerically indexed list.

<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo.field import Array</code></p></dd>
	<dt><h5>Inherits</h5></dt><dd><p><code>marrow.mongo:<strong>Field</strong></code></p></dd>
</dl>


## Attributes

This field type inherits all [`Field` attributes](field.md#attributes). As a complex type, the first positional argument is always the nested field instance, other positional ordering is unaffected.

<dl>
	<dt><h5><code>kind</code></h5></dt><dd>
		<p>A <code>Field</code> subclass instance, or an instance of <code>Field</code> itself if the type is dynamic.</p>
		<p><label>Required</label></p>
	</dd>
</dl>


## Usage

Instantiate and assign an instance of this class during construction of a new `Document` subclass, passing another `Field` instance representing the type to embed as the first positional parameter. Accessing as a class attribute will return a Queryable allowing array-like filtering operations, and access as an instance attribute will return a `list` subclass containing cast values.

To reduce boilerplate when costructing new document instances utilizing `Array` fields, if the `assign` attribute is truthy and no default is otherwise assigned, an empty list will be assumed and assigned, eliminating the need for armour against None or non-existant conditions.


## Examples

#### Arrays of Scalar Values

{% method -%}
Tags are a very, very common storage pattern, modelled here using an `Array` of free-form `String` values. Foreign references are also common, though MongoDB itself provides no referential integrity validation.

{% sample lang="python" -%}
```python
class Record(Document):
	tags = Array(String(), assign=True)
	actors = Array(Reference('Account'))
```
{% endmethod %}


#### Array of Embedded Documents

{% method -%}
Another principal pattern is that of an array of embedded documents, for example, an invoice with line items.

{% sample lang="python" -%}
```python
class Invoice(Document):
	class Item(Document):
		...
	
	items = Array(Embed(Item), assign=True)
```
{% endmethod %}


## See Also

* [`Embed`](embed.md)
* [`Reference`](reference.md)
