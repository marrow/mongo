# Field

{% method -%}
A `Field` represents a data types storable within MongoDB and the associated machinery for access, querying, and manipulation. It is the common base class for almost all field types and can be used standalone to represent a "dynamic" field.

<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo import Field</code></p></dd>
	<dt><h5>Inherits</h5></dt><dd><p><code>marrow.schema:<strong>Attribute</strong></code></p></dd>
</dl>

{%common -%}

#### Contents

1. [Attributes](#attributes)
2. [Metadata](#metadata)
2. [Usage](#usage)
3. [Examples](#examples)
4. [See Also](#see-also)

{% endmethod %}


## Attributes

<dl>
	<dt><h5><code>name</code></h5></dt><dd>
		<p>The database-side name of the field, stored internally as the metadata property <code>__name__</code>.</p>
		<p>Default calculated when assigned as a class attribute from the name given to the <code>Field</code> instance during class construction.</p>
	</dd><dt><h5><code>default</code></h5></dt><dd>
		<p>The default value to utilize if the field is missing from the backing store. You may assign a callback routine returning a value to utilize instead.</p>
	</dd><dt><h5><code>choices</code></h5></dt><dd>
		<p>The permitted set of values as a sequence; may be static or a dynamic, argumentless callback routine as per <code>default</code>.</p>
		<p><label>Default</label><code>None</code></p>
	</dd><dt><h5><code>required</code></h5></dt><dd>
		<p>Must have a value assigned. <code>None</code>, an empty string, and other falsy values are acceptable.</p>
		<p><label>Default</label><code>False</code></p>
	</dd><dt><h5><code>nullable</code></h5></dt><dd>
		<p>If <code>True</code>, will store <code>None</code>. If <code>False</code>, will store any non-<code>None</code> default, or remove the field from the backing store.</p>
		<p><label>Default</label><code>False</code></p>
	</dd><dt><h5><code>exclusive</code></h5></dt><dd>
		<p>The set of other fields that must <strong>not</strong> be set for this field to be writeable.</p>
		<p><label>Default</label><code>None</code></p>
	</dd>
</dl>


#### Local Manipulation

Define how Python-side code interacts with the stored MongoDB data values.

<dl>
	<dt><h5><code>transformer</code></h5></dt><dd>
		<p>A Marrow Schema <code>Transformer</code> class to use when loading or storing values.</p>
		<p><label>Default</label><code>FieldTransform()</code></p>
	</dd><dt><h5><code>validator</code></h5></dt><dd>
		<p>A Marrow Schema <code>Validator</code> class to use when validating values during assignment.</p>
		<p><label>Default</label><code>Validator()</code></p>
	</dd><dt><h5><code>assign</code></h5></dt><dd>
		<p>Automatically assign the default value to the backing store when constructing a new instance or the value is found to be missing on access.</p>
		<p><label>Default</label><code>False</code></p>
	</dd>
</dl>


#### Predicates

These are either argumentless callback routines returning, or simply the constant values:

* `None`  
  Interpreted as "no opinion", with the fallback being to deny or exclude.

* `False` (or falsy)  
  Explicitly forbid, deny, or exclude.

* `True` (or truthy)  
  Explicitly allow or include.

These are used to restrict or define security-like behaviours.

<dl>
	<dt><h5><code>positional</code></h5></dt><dd>
		<p>Permit this field to be populated through positional assignment during instantiation of its containing class.</p>
		<p><label>Default</label><code>True</code></p>
	</dd><dt><h5><code>repr</code></h5></dt><dd>
		<p>Include this field in the programmers' representation, primarily utilized for REPL shells, logging, tracebacks, and other diagnostic purposes.</p>
		<p><em>Protect sensitive fields from accidental exposure by assigning <code>False</code>.</em></p>
		<p><label>Default</label><code>True</code></p>
	</dd><dt><h5><code>project</code></h5></dt><dd>
		<p>Inlcude (or exclude) this field from the default projection.</p>
		<p><label>Default</label><code>None</code></p>
	</dd><dt><h5><code>read</code></h5></dt><dd>
		<p>Permission to read values from this field.</p>
		<p><em>Not internally enforced.</em></p>
		<p><label>Default</label><code>True</code></p>
	</dd><dt><h5><code>write</code></h5></dt><dd>
		<p>Permission to assign values to this field.</p>
		<p><em>Not internally enforced.</em></p>
		<p><label>Default</label><code>True</code></p>
	</dd><dt><h5><code>sort</code></h5></dt><dd>
		<p>Allow sorting/ordering on this field.</p>
		<p><em>Not internally enforced.</em></p>
		<p><label>Default</label><code>True</code></p>
	</dd>
</dl>


## Metadata

Class-level metadata attributes meant for use when subclassing.

<dl>
	<dt><h5><code>__name__</code></h5></dt><dd>
		<p>The database-side name of this field instance.</p>
		<p><label>Read-Only</label></p>
	</dd><dt><h5><code>__allowed_operators__</code></h5></dt><dd>
		<p>The permissable MongoDB filter and update operators, or hash-prefixed groups of operations.</p>
		<p><label>Type</label><code>set</code></p>
	</dd><dt><h5><code>__disallowed_operators__</code></h5></dt><dd>
		<p>Specific operations may be excluded from group-based inclusion, if utilized above.</p>
		<p><label>Type</label><code>set</code></p>
	</dd><dt><h5><code>__document__</code></h5></dt><dd>
		<p>A weak reference to the document the instance is bound to; automatically popualted.</p>
		<p><label>Read-Only</label></p>
	</dd><dt><h5><code>__foreign__</code></h5></dt><dd>
		<p>The MongoDB stored datatype, as defined by the <a href="https://docs.mongodb.com/manual/reference/operator/query/type/#available-types"><code>$type</code> operator</a>.</p>
		<p><label>Type</label><code>str</code></p>
	</dd>
</dl>


## Usage



## Examples

