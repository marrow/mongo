# Document

This is the top-level class your own document schemas should subclass. They may also subclass each-other; field declaration order is preserved, with subclass fields coming after those provided by the parent class(es). Any fields redefined will have their original position preserved. Fields may be disabled in subclasses by assigning `None` to the attribute within the subclass; this is not recommended, though supported to ease testing.
	
	<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo import Document</code></p></dd>
	<dt><h5>Inherits</h5></dt><dd><p><code>marrow.schema:<strong>Container</strong></code></p></dd>
</dl>


## Attributes

The `Document` base class is a Marrow Schema [`Container`](https://github.com/marrow/schema#32-container), a type of declarative [`Element`](https://github.com/marrow/schema#31-element) which is designed to contain other Elements. There are a number of attributes and a few special methods available to these "declarative" objects described in that project's README. Beyond those, `Document` defines:

<dl>
	<dt><h5><code>__store__</code></h5></dt><dd>
		<p>The underlying storage type to utilize for the `__data__` attribute.</p>
		<p><label>Required</label></p>
		<p><label>Default</label><code>odict</code></p>
	</dd><dt><h5><code>__foreign__</code></h5></dt><dd>
		<p>A set representing the in-database stored type alias(es) instances of this can/are be represented as.</p>
		<p><label>Reference</label><a href="https://docs.mongodb.com/manual/reference/operator/query/type/#available-types">MongoDB $type → Behavior → Available Types</a></p>
		<p><label>Required</label></p>
		<p><label>Default</label><code>{'object'}</code></p>
	</dd><dt><h5><code>__type_store__</code></h5></dt><dd>
		<p>When assigned as an embedded document, utilize this field to store a reference to the class used to dereference the document. One example approach is that taken by the <code>Derived</code> trait.</p>
		<p><label>Default</label><code>None</code></p>
	</dd><dt><h5><code>__pk__</code></h5></dt><dd>
		<p></p>
		<p><label>Required</label></p>
		<p><label>Default</label><code></code></p>
		<p><label>Added</label><code>&gt;=1.1.2</code></p>
	</dd>
</dl>


## Usage

Beyond the basic `Container` behaviour, `Document` allows for choice in underlying storage type used in the construction of the `__data__` attribute, defaulting to `odict`.

## Usage