# Basic Field Datatypes

1. [Binary](#binary)
2. [Date](#date)
3. [ObjectId](#objectid)
4. [Regex](#regex)
5. [String](#string)
6. [TTL](#ttl)
7. [Timestamp](#timestamp)


## Binary

{% method -%}


{% sample lang="python" -%}
```python
from marrow.mongo.field import Binary
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

Two additional arguments are provided to control automatic string transformation when using the default transformer.

{% sample lang="python" -%}
```python
from marrow.mongo.field import String

class MyDocument(Document):
	string = String(strip=False, case=None)
```
{% endmethod %}

* **`strip`**

  Defaulting to `False`, if this is `True` then a bare call to `.strip()` will be made after unicode string casting. If another truthy value is provided it will be used as the argument to the `.strip()` call.

* **`case`**

  This allows for automatic case conversion when values are assigned to the field. If the value is `1`, `True`, `'u'`, or `'upper'` then any value assigned will have `.upper()` called after typecasting. If the value is `-1`, `False`, `'l'`, or `'lower'` then the value assigned will have `.lower()` called after typecasting. You may also use `'t'` or `'title'` to utilize `.title()` respectively.

Subclasses may utilize `super()` to invoke this standaard behaviour within overridden `to_native` and `to_foreign` methods.

## TTL

{% method -%}


{% sample lang="python" -%}
```python
from marrow.mongo.field import TTL
```
{% endmethod %}


## Timestamp

{% method -%}


{% sample lang="python" -%}
```python
from marrow.mongo.field import Timestamp
```
{% endmethod %}
