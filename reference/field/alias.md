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
		<p>A string reference to another field in the same containing class. See the [Usage](#usage) section below for the structure of these references.</p>
		<p><label>Required</label></p>
	</dd><dt><h5><code>deprecate</code></h5></dt><dd>
		<p>Used to determine if access should issue `DeprecationWarning` messages. If truthy, a warning will be raised, and if non-boolean the string value will be included in the message.</p>
		<p><label>Default</label><code><code>False</code></code></p>
	</dd><dt><h5><code></code></h5></dt><dd></dd>
</dl>


## Usage






## Example


## See Also
