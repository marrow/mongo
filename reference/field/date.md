# Date

{% method -%}
Date fields store `datetime` values.  Times are always stored in UTC, though with appropriate support packages installed (`pytz` and/or `tzlocal`) this can include timezone support.

<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo.field import Date</code></p></dd>
	<dt><h5>Inherits</h5></dt><dd><p><code>marrow.mongo:<strong>Field</strong></code></p></dd>
		<p><label>Available</label><code>&gt;=1.1.2</code></p>
</dl>

{%common -%}

#### Contents

1. [Attributes](#attributes)
2. [Usage](#usage)
3. [Examples](#examples)

{% endmethod %}


## Attributes

This field type inherits all [`Field` attributes](field.md#attributes) and represents a singular, scalar date/time value.

<dl>
	<dt><h5><code>naive</code></h5></dt><dd>
		<p>Timezone to interpret naive `datetime` objects as utilizing.</p>
		<p><label>Default</label><code>utc</code></p>
		<p><label>Added</label><code>&gt;=1.1.3</code></p>
	</dd><dt><h5><code>tz</code></h5></dt><dd>
		<p>Timezone to cast to when retrieving from the database.</p>
		<p><label>Default</label><code>()</code></p>
		<p><label>Added</label><code>&gt;=1.1.3</code></p>
	</dd>
</dl>

Timezone references as utilized by the above may be any of:

* The constant string `"naive"`, resulting in no timezone transformation or alteration of the `tzinfo` attribute at all.
* The constant string `"local"`, auto-detecting the host's timezone, requiring the package `localtz` be installed. This is most useful if you use `datetime.now()` instead of `datetime.utcnow()`—please consider updating your code to utilize the UTC variant in preference to this.
* A `tzinfo` object, such as those provided by the `pytz` package.

Any use of timezone awareness will require the `pytz` package be installed, as Python's built-in `tzinfo` objects suffer a number of issues. Note also that use of timezones comes with a performance penalty.

## Usage

Instantiate and assign an instance of this class during construction of a new `Document` subclass. Accessing as a class attribute will return a Queryable allowing filtering operations, and access as an instance attribute will return a `datetime` cast value.

Date fields are highly aware of date-like objects and how to apply them. For example, you may provide any of the following in place of a pure `datetime` value:

* Any `MutableMapping` instance (such as a `dict` or `Document` instance) with an `_id` key whose value is an `ObjectId`. The date/time value will be pulled automatically from the `_id.generation_time`.
* A bare BSON `ObjectId` instance, behaving as above.
* A `datetime.timedelta` instance whose value will be immediately applied (added to) the result of `datetime.utcnow()`.
* A `datetime` instance.

## Examples

### Typecasting Behaviour and Querying

{% method -%}
A key reason for the above typecasting allowances are to permit natural comparison against those types of objects as admittedly, it'll be unlikely you'll need to populate a date from the ID of a record.

Given a Date field named `modified`, you can identify all documents modified in the last 30 days easily and without performing date math yourself: (remembering that the value being queried for becomes static after that comparison)

{% sample lang="python" -%}
```python
query = Asset.modified >= timedelta(days=-30)
Asset.find(query)
```
{% endmethod %}

