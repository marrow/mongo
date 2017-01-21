# Basic Field Datatypes

{% method -%}
Fields which represent scalar (singular) values are referred to as _basic fields_.

{% sample lang="python" -%}
1. [Binary](#binary)
2. [Date](#date)
3. [ObjectId](#objectid)
4. [Regex](#regex)
5. [String](#string)
6. [TTL](#ttl)
7. [Timestamp](#timestamp)
{% endmethod %}


## Binary

{% method -%}
A binary string. In Python 3 this is represented as a `bytes` instance, under Python 2 this reads and writes `str` instances. To support binary serialization, it may be useful to implement callables implementing the Marrow Schema transformer protocol and specify them using the `transformer` argument.

Large binary (BLOB) data exceeding a few hundred kilobytes should instead be stored using GridFS.

{% sample lang="python" -%}
```python
from marrow.mongo.field import Binary

class MyDocument(Document):
	binary = Binary()
```
{% endmethod %}


## Date

{% method -%}


{% sample lang="python" -%}
```python
from marrow.mongo.field import Date
```
{% endmethod %}


## ObjectId

{% method -%}


{% sample lang="python" -%}
```python
from marrow.mongo.field import ObjectId
```
{% endmethod %}


## Regex

{% method -%}


{% sample lang="python" -%}
```python
from marrow.mongo.field import Regex
```
{% endmethod %}


## String

{% method -%}
Unicode text stored as a UTF-8 encoded binary string. In Python 3 this is represented as a `str` instance, under Python 2 this reads and writes `unicode` instances. For additional details, see the [BSON type reference for strings](https://docs.mongodb.com/manual/reference/bson-types/#string) from the MongoDB manual.

Subclasses may utilize `super()` to invoke this standaard behaviour within overridden `to_native` and `to_foreign` methods.

{% sample lang="python" -%}
```python
from marrow.mongo.field import String

class MyDocument(Document):
	string = String(strip=False, case=None)
```
{% endmethod %}

#### Arguments

<dl>
	<dt>
		<h5 id="string-argument-strip"><code>strip</code></h5>
		<small>optional</small>
	</dt><dd>
		<p>
			If this is <code>True</code> then a bare call to <code>.strip()</code> will be made after unicode string casting. If another truthy value is provided it will be used as the argument to the <code>.strip()</code> call.
		</p>
		<p>
			<label>Default</label><code>False</code>
		</p>
	</dd>
	<dt>
		<h5 id="string-argument-case"><code>case</code></h5>
		<small>optional</small>
	</dt><dd>
		<p>
			Allows for automatic case conversion during value assignment. If <code>case</code> is <code>1</code>, <code>True</code>, <code>'u'</code>, or <code>'upper'</code> then any value assigned will have <code>.upper()</code> called after typecasting. If the value is <code>-1</code>, <code>False</code>, <code>'l'</code>, or <code>'lower'</code> then the value assigned will have <code>.lower()</code> called after typecasting. You may also use <code>'t'</code> or <code>'title'</code> to utilize <code>.title()</code> respectively.
		</p>
		<p>
			<label>Default</label><code>None</code>
		</p>
	</dd>
</dl>


## TTL

{% method -%}
To assist with the use of [MongoDB Time-to-Live indexes]() a `TTL` field is provided as a specialization of the general [`Date`](#date) field. It accepts a range of datatypes for automatic casting to an absolute time upon assignment, detailed below.

Subclasses may utilize `super()` to invoke standaard casting behaviour within overridden `to_native` and `to_foreign` methods.

{% sample lang="python" -%}
```python
from marrow.mongo.field import TTL

class MyDocument(Document):
	when = TTL()
```
{% endmethod %}

#### Accepted Values

<dl>
	<dt>
		<h5 id="ttl-value-timedelta"><code>timedelta</code></h5>
	</dt><dd>
		<p>
			Assignment of a <code>timedelta</code> instance will result in the storage of `datetime` representing the current time in UTC modified by that delta through addition.
		</p>
	</dd>
	<dt>
		<h5 id="ttl-value-datetime"><code>datetime</code></h5>
	</dt><dd>
		<p>
			Any explicit <code>datetime</code> will be utilized unmodified.
		</p>
	</dd>
	<dt>
		<h5 id="ttl-value-number">numbers</h5>
	</dt><dd>
		<p>
			Assigning any numeric value (i.e. <code>int</code>, <code>float</code>) will interpret that as the <code>days</code> argument to <code>timedelta</code>, applied as per a <code>timedelta</code> described above.
		</p>
	</dd>
</dl>


## Timestamp

{% method -%}


{% sample lang="python" -%}
```python
from marrow.mongo.field import Timestamp
```
{% endmethod %}
