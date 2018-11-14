# Index

An `Index` represents a MongoDB database index, of any kind.

<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo import Index</code></p></dd>
	<dt><h5>Inherits</h5></dt><dd><p><code>marrow.schema:<strong>Attribute</strong></code></p></dd>
</dl>


## Attributes

Indexes are defined via the following attributes predominantly used as [arguments to the eventual `createIndex` call](https://docs.mongodb.com/manual/reference/method/db.collection.createIndex/). The field references to include in the index are passed positionally, all other attributes may be passed as keyword arguments. Not all are utilized for each type of index, see the usage section below (or relevant MongoDB documentation for the index type) for details.

<dl>
	<dt><h5><code>fields</code></h5></dt><dd>
		<p>A set of field references and their associated prefixes as strings. Initially defined as the positional arguments to the class constructor.</p>
		<p><label>Required</label></p>
	</dd><dt><h5><code>unique</code></h5></dt><dd>
		<p>Should the index be constructed with a unique constraint?</p>
		<p><label>Default</label><code>False</code></p>
		<p><label>Official Documentation</label><a href="https://docs.mongodb.com/manual/core/index-unique/">Unique Indexes</a></p>
	</dd><dt><h5><code>background</code></h5></dt><dd>
		<p>Create the index as a background operation. Note that if this is falsy, the foreground index build will block all other operations on the database.</p>
		<p><label>Default</label><code>True</code></p>
		<p><label>Official Documentation</label><a href="https://docs.mongodb.com/manual/reference/method/db.collection.createIndex/#behaviors">db.collection.createIndex() Behaviours</a></p>
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
		<p>Bucket size for use with, and only appropriate for, geoHaystack indexes.</p>
		<p><label>Official Documentation</label><a href="https://docs.mongodb.com/manual/core/geohaystack/">geoHaystack Indexes</a></p>
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

Define your document subclass and assign instances of `Index` as attributes. The name of the attribute will be used as the MongoDB index name. To avoid potential collisions with fields or other attributes such as methods, it is recommended to prefix these attribute names with a single leading underscore.

```python
from marrow.mongo import Document, Index
from marrow.mongo.field import String, Integer

class Person(Document):
	name = String()
	age = Integer()
	
	_age = Index('age')
```

You can then create the index by calling the `create` method of the `Index` object, passing in a collection:

```python
import pymongo

# Connect and retrieve a handle to the target collection.
client = pymongo.MongoClient('mongodb://localhost/')
db = client.test
collection = db.people

# Create an index in that collection.
Person._age.create(collection)
```

If you are using any of the mix-in traits descendant from `Collection` (such as `Queryable`) then the `create_collection` method will, by default, also discover and create any associated indexes.

```python
from marrow.mongo.trait import Queryable

class WikiPage(Queryable, Document):
	__collection__ = 'pages'
	
	id = String('_id')
  content = String()
	
  _fti = Index('$content')

WikiPage.bind(db)  # Permit ActiveRecord-like usage.
WikiPage.create_collection()

# Alternatively, this can be called to create any missing indexes.
# WikiPage.create_indexes()
```

## Methods

* `adapt(*args, **kw)` — create a new copy of this index with adjustments applied. Takes the same arguments as the constructor, with any new fields declared being added to the existing set.
* `create(collection, **kw)` — instruct MongoDB to construct and persist the index. If the index is not configured for `background` construction, this will block other operations on the database until complete. Additional arguments are passed through to the eventual PyMongo `collection.create_index` call. Also available via the PyMongo standard method name, `create_index`.
* `drop(collection)` — instruct MongoDB to deconstruct and remove the index from the collection metadata. Also available via the PyMongo standard method name, `drop_index`.