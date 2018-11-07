# Binary

{% method -%}
String fields store Unicode text, utilizing the native Unicode representation for your version of Python.  (On Python 2: `unicode`, on Python 3: `str`.)

<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo.field import String</code></p></dd>
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

This field type inherits all [`Field` attributes](field.md#attributes) and represents a singular, scalar Unicode string
value.  In addition to the basic attributes, String fields can automatically strip extraneous whitespace on assignment
or perform case normalization, e.g. automatic execution of `str.upper()`, `str.lower()`, or `str.title()`.

<dl>
	<dt><h5><code>strip</code></h5></dt><dd>
		<p>Either the boolean literal `True` or a string representing the argument to `str.strip`, that is, the characters to strip.</p>
		<p><label>Default</label><code>False</code></p>
		<p><label>Added</label><code>&gt;=1.1.1</code></p>
	</dd><dt><h5><code>case</code></h5></dt><dd>
		<p>Truthy values (or the string literal `"u"` or `"upper"`) will request uppercase normalization, falsy values (or the literals `"l"` or `"lower"`) request lowercase normalization, or the literal `"title"` can be used to request title case.</p>
		<p><label>Default</label><code>None</code></p>
		<p><label>Added</label><code>&gt;=1.1.1</code></p>
	</dd>
</dl>


## Usage

Instantiate and assign an instance of this class during construction of a new `Document` subclass. Accessing as a class attribute will return a Queryable allowing string filtering operations, and access as an instance attribute will return a `str` (or `unicode` on Python 2) cast value.


## See Also

* [`Binary`](binary.md)
