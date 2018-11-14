# Index

An `Index` represents a MongoDB database index, of any kind.

<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo import Index</code></p></dd>
	<dt><h5>Inherits</h5></dt><dd><p><code>marrow.schema:<strong>Attribute</strong></code></p></dd>
</dl>


## Attributes

In the order they can be passed positionally during construction, indexes are defined via the following attributes predominantly used as [arguments to the eventual `createIndex` call](https://docs.mongodb.com/manual/reference/method/db.collection.createIndex/). Not all are utilized for each type of index, see the usage section below (or MongoDB documentation for `createIndex`) for details.

<dl>
	<dt><h5><code>fields</code></h5></dt><dd>
		<p>A set of field references and their prefixes (sort order) as strings.</p>
		<p><label>Required</label></p>
	</dd><dt><h5><code>unique</code></h5></dt><dd>
		<p>Should the index be constructed with a unique constraint?</p>
		<p><label>Default</label><code>False</code></p>
		<p><label>Official Documentation</label><a href="https://docs.mongodb.com/manual/core/index-unique/">Unique Indexes</a></p>
	</dd><dt><h5><code>background</code></h5></dt><dd>
		<p>Create the index as a background operation. Note that if this is falsy, the foreground index build will [block all other operations on the database](https://docs.mongodb.com/manual/reference/method/db.collection.createIndex/#behaviors).</p>
		<p><label>Default</label><code>True</code></p>
  </dd><dt><h5><code>sparse</code></h5></dt><dd>
		<p>Omit from the index documents that omit the field.</p>
		<p><label>Default</label><code>False</code></p>
		<p><label>Official Documentation</label><a href="https://docs.mongodb.com/manual/core/index-sparse/">Sparse Indexes</a></p>
  </dd><dt><h5><code>expire</code></h5></dt><dd>
		<p>Number of seconds after which to expire (cull/delete/remove) the record, declaring a "time-to-live" (TTL) index.</p>
		<p><label>Official Documentation</label><a href="https://docs.mongodb.com/manual/core/index-ttl/">TTL Indexes</a></p>
  </dd><dt><h5><code>partial</code></h5></dt><dd>
		<p>A query filter (raw, or as constructed by field comparison or use of parametric helper) to use for partial indexing.</p>
		<p><label>Official Documentation</label><a href="https://docs.mongodb.com/manual/core/index-partial/">Partial Indexes</a></p>
  </dd><dt><h5><code>bucket</code></h5></dt><dd>
		<p>Bucket size for use with, and only appropriate for, [geoHaystack indexes](https://docs.mongodb.com/manual/core/geohaystack/).</p>
  </dd><dt><h5><code>min</code></h5></dt><dd>
		<p>The lower inclusive boundary for the longitude and latitude values.</p>
		<p><label>Default</label><code>-180.0</code></p>
  </dd><dt><h5><code>max</code></h5></dt><dd>
		<p>The upper inclusive boundary for the longitude and latitude values.</p>
		<p><label>Default</label><code>180.0</code></p>
	</dd>
</dl>


## Referencing Fields

Fields are referenced by their "attribute path", that is, a period-separated string representing the path to that field from the top-level Document class.  For example, if you define a model with a `name = Field('foo')` field, the path for this is `"name"`.  If you have an embedded document, say, an `Address` with a `city` field attached as `addr = Embed(Address)`, referencing the City would be: `"addr.city"`

Beyond just the reference, indexes also use prefix symbols to identify the type of index, ordering, etc.


### Index Prefixes

* *No prefix* or `+` — Ascending
* `-` — Descending
* `@` — Geo2D
* `%` — GeoHaystack
* `*` — GeoSphere
* `#` — Hashed
* `$` — Full Text


## Usage



## Examples

