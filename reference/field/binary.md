# Binary

{% method -%}
Binary fields store, as the name implies, raw binary data. This is the rough equivalent to a BLOB field in relational
databases. The amount of storage space [**is
limited**](https://docs.mongodb.com/manual/reference/limits/#bson-documents) to 16MB per document. For storage of
binray data beyond this limit please utilize [GridFS](https://docs.mongodb.com/manual/core/gridfs/index.html) support.

<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo.field import Binary</code></p></dd>
	<dt><h5>Inherits</h5></dt><dd><p><code>marrow.mongo:<strong>Field</strong></code></p></dd>
</dl>

{%common -%}

#### Contents

1. [Attributes](#attributes)
2. [Usage](#usage)
3. [Examples](#examples)
4. [See Also](#see-also)

{% endmethod %}


## Attributes

This field type inherits all [`Field` attributes](field.md#attributes) and represents a singular, scalar binary string
value. It has no specific configuration options.


## Usage

Instantiate and assign an instance of this class during construction of a new `Document` subclass. Accessing as a class attribute will return a Queryable allowing binary string filtering operations, and access as an instance attribute will return a `bytes` cast value.


## Example

{% method -%}
Users may wish to utilize a "profile image" to identify themselves. Utilizing a Binary field (and appropriate upload limits) can facilitate this. When presenting back via HTTP, the mime type would be useful to track; see GridFS for this capability as well.

{% sample lang="python" -%}
```python
class User(Document):
	name = String('_id')
	avatar = Binary()

me = User("amcgregor")

with open('avatar.png', 'rb') as fh:
	me.avatar = fh.read()

me.insert_one()
```
{% endmethod %}


## See Also

* [`String`](string.md)

