# Alias

{% method -%}
An **Alias** is a proxy to another field, potentially nested, within the same document.

Utilizing an Alias allows class-level querying and instance-level read access, write access under most conditions, as well as optional deprecation warning generation.

<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo.field import Alias</code></p></dd>
	<dt><h5>Inherits</h5></dt><dd><p><code>marrow.schema:<strong>Attribute</strong></code></p></dd>
	<dt><h5>Added</h5></dt><dd><p><code>1.1.0</code> <a href="https://github.com/marrow/mongo/releases/tag/1.1.0">Oranir</a></p></dd>
	<dt><h5></h5></dt><dd><p><code></code></p></dd>
</dl>

{%common -%}

#### Table of Contents

1. [Attributes](#attributes)
2. [Usage](#usage)
3. [Example](#example)
4. [See Also](#see-also)

{% endmethod %}


## Attributes

This pseudo-field **does not** inherit other field attributes.

<dl>
	<dt><h5><code>path</code></h5></dt><dd>
		<p>A string reference to another field in the same containing class. See the <a href="#usage">Usage</a> section below for the structure of these references.</p>
		<p><label>Required</label></p>
	</dd><dt><h5><code>deprecate</code></h5></dt><dd>
		<p>Used to determine if access should issue <code>DeprecationWarning</code> messages. If truthy, a warning will be raised, and if non-boolean the string value will be included in the message.</p>
		<p><label>Default</label><code><code>False</code></code></p>
	</dd><dt><h5><code></code></h5></dt><dd></dd>
</dl>


## Usage

References to other fields may be simple and direct, nested, or may even reference specific array elements during resolution. Access this way may be intentional or to support legacy code. This pseudo-field utilizes the Marrow Package `traverse` utility to allow it to resolve a wide variety of attributes.

References to other fields may be:

* Simple string names of sibling attributes.
* The "path" to a descendant attribute of a sibling.
* A "path" involving numeric array indexes.
* A "path" involving dictionary key references.

Paths are strings comprised of dot-separated attribute names. The search beings at the containing document, consuming path elements as we go. Each path element is first attempted as an attribute and, failing that, will attempt dictionary access. If the path element is numeric, it will be utilized as an array index.

Attributes (and dictionary keys) prefixed with an underscore are protected and will not resolve.

Accessing an Alias at the class level will resolve a Queryable for the target field, allowing filter document construction through comparison utilizing the alias name itself. On an instance access will retrieve or assign the value of the target field.


## Example

### Simple Sibling Reference

{% method -%}
{% sample lang="python" -%}
```python
```
{% endmethod %}


### Descendant Attriute of a Sibling

{% method -%}
{% sample lang="python" -%}
```python
```
{% endmethod %}


### Numeric Array Index Reference

{% method -%}
{% sample lang="python" -%}
```python
```
{% endmethod %}


### Legacy Alternative Names / Deprecation

{% method -%}
{% sample lang="python" -%}
```python
```
{% endmethod %}


## See Also

* 
