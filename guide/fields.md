# Fields

Included with Marrow Mongo are field types covering all core types supported by MongoDB. A class model is used to define new field types, with a large amount of functionality provided by the base `Field` class itself. This base class is directly usable where the underlying field type is dynamic or not known prior to access.

```python
from marrow.mongo import Field
```


## Field Name Mapping

{% method -%}
In general, basic fields accept one positional parameter: the name of the database-side field to store data against. In the following example any attempt to read or write to the `field` attriute of a `MyDocument` instance will instead retrieve data from the backing document using the key `name`.

{% sample lang="python" -%}
```python
class MyDocument(Document):
	field = Field('name')
```
{% endmethod %}

