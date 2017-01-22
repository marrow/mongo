# Complex Field Datatypes
{% method -%}
_Complex fields_ are meta-fields or fields whose value is a compound structure, such as a embedded document, array, or reference.

{% sample lang="python" -%}
#### Table of Contents

1. [Alias](#alias)
2. [Array](#array)
3. [Embed](#embed)
4. [PluginReference](#pluginreference)
5. [Reference](#reference)

{% endmethod %}


## Alias

{% method -%}
A meta-field to reference a field, potentially nested, elsewhere in the document. This provides a shortcut for querying nested fields, e.g. to more easily access the latitude and longitude of a GeoJSON point, as in the following example.

Attempts to read or write `latitude` and `longitude` on instances of `MyGeoJSONPoint`, as well as attempts to query the nested values through class attribute access, will be forwarded on to the respective referenced field.

{% sample lang="python" -%}
```python
from marrow.mongo.field import String, Array, Number, Alias

class MyGeoJSONPoint(Document):
	kind = String('type', default='point', assign=True)
	coordinates = Array(Number(), default=lambda: [0, 0], assign=True)
	latitude = Alias('coordinates.1')
	longitude = Alias('coordinates.0')
```
{% endmethod %}


## Array

{% method -%}


{% sample lang="python" -%}
```python
from marrow.mongo.field import Array
```
{% endmethod %}


## Embed

{% method -%}


{% sample lang="python" -%}
```python
from marrow.mongo.field import Embed
```
{% endmethod %}


## PluginReference

{% method -%}


{% sample lang="python" -%}
```python
from marrow.mongo.field import PluginReference
```
{% endmethod %}


## Reference

{% method -%}


{% sample lang="python" -%}
```python
from marrow.mongo.field import Reference
```
{% endmethod %}

