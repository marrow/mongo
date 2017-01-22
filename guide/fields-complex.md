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

#### Accepted Values

<dl>
	<dt>
		<h5 id="objectid-value-bson-objectid">BSON <code>ObjectId</code></h5>
	</dt><dd>
		<p>
			Assigning or comparing an existing BSON <code>ObjectId</code> instance will utilize it unmodified.
		</p>
	</dd>
	<dt>
		<h5 id="objectid-value-datetime"><code>datetime</code></h5>
	</dt><dd>
		<p>
			Assignment of or comparison against a <code>datetime</code> object will result in the generation of a pseudo-BSON <code>ObjectId</code> with only the generation time field filled. This is useful for range comparison, to select for documents based on creation time.
		</p>
	</dd>
	<dt>
		<h5 id="objectid-value-timedelta"><code>timedelta</code></h5>
	</dt><dd>
		<p>
			As per <code>datetime</code> above, utilizing a <code>datetime</code> object generated as the addition of the delta to the current time in UTC.
		</p>
	</dd>
	<dt>
		<h5 id="objectid-value-"><em>document</em></h5>
	</dt><dd>
		<p>
			Use of a dictionary or dictionary-alike (such as a <code>Document</code> instance) with an assigned <code>_id</code> key will utilize the value of that key automatically after casting with the BSON <code>ObjectId</code> type.
		</p>
	</dd>
	<dt>
		<h5 id="objectid-value-"><em>other values</em></h5>
	</dt><dd>
		<p>
			Other values will be cast as unicode strings, then cast using the BSON <code>ObjectId</code> type.
		</p>
	</dd>
</dl>


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

