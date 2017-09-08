# Collection

## Metadata


### Collection Binding

<dl>
	<dt>
		<h5 id="default-values-assign"><code>__bound__</code></h5>
	</dt><dd>
		<p>
			The pyMongo Collection instance this class is bound to, or `None` if not bound. Primarily meant to be used as a truthy value; utilize `.get_collection()` to acquire a handle to the pyMongo Collection if intended for use.
		</p>
		<p>
			<label>Default</label><code>None</code>
		</p>
	</dd>
	<dt>
		<h5 id="default-values-assign"><code>__collection__</code></h5>
	</dt><dd>
		<p>
			The string name of the collection to bind to. Can be used as a truthy value to identify if a `Document` class is top-level or not.
		</p>
		<p>
			<label>Default</label><code>None</code>
		</p>
	</dd>
	<dt>
		<h5 id="default-values-assign"><code>__projection__</code></h5>
	</dt><dd>
		<p>
			A **read-only** calculated property generated at class construction time identifying the default projection to utilize. This is derived from the available fields and their `project` predicates.
		</p>
	</dd>
</dl>

### Data Access Options

<dl>
	<dt>
		<h5 id="default-values-assign"><code>__read_preference__</code></h5>
	</dt><dd>
		<p>
			The default read preference to utilize when binding. Must be an appropriate attribute value of the PyMongo [`ReadPreference`](http://api.mongodb.com/python/current/api/pymongo/read_preferences.html#pymongo.read_preferences.ReadPreference) object or customized instance of a [`read_preferences`](http://api.mongodb.com/python/current/api/pymongo/read_preferences.html#pymongo.read_preferences.ReadPreference) class.
		</p>
		<p>
			<label>Default</label><code>ReadPreference.PRIMARY</code>
		</p>
	</dd>
	<dt>
		<h5 id="default-values-assign"><code>__read_concern__</code></h5>
	</dt><dd>
		<p>
			The read concern (level of isolation) to utilize when binding. Must be a PyMongo [`ReadConcern`](http://api.mongodb.com/python/current/api/pymongo/read_concern.html) instance.
		</p>
		<p>
			<label>Default</label><code>ReadConcern(level=None)</code>
		</p>
	</dd>
	<dt>
		<h5 id="default-values-assign"><code>__write_concern__</code></h5>
	</dt><dd>
		<p>
			The default write concern (level of confirmation) to utilize when binding. Must be a PyMongo [`WriteConcern`](http://api.mongodb.com/python/current/api/pymongo/write_concern.html) instance.
		</p>
		<p>
			<label>Default</label><code>WriteConcern(w=1, wtimeout=None, j=None, fsync=None)</code>
		</p>
	</dd>
</dl>

### Storage Options

<dl>
	<dt>
		<h5 id="default-values-assign"><code>__collection__</code></h5>
	</dt><dd>
		<p>
			
		</p>
		<p>
			<label>Default</label><code>None</code>
		</p>
	</dd>
	<dt>
		<h5 id="default-values-assign"><code>__collection__</code></h5>
	</dt><dd>
		<p>
			
		</p>
		<p>
			<label>Default</label><code>None</code>
		</p>
	</dd>
</dl>









<dl>
	<dt>
		<h5 id="default-values-assign"><code>__collection__</code></h5>
	</dt><dd>
		<p>
			
		</p>
		<p>
			<label>Default</label><code>None</code>
		</p>
	</dd>
	<dt>
		<h5 id="default-values-assign"><code>__collection__</code></h5>
	</dt><dd>
		<p>
			
		</p>
		<p>
			<label>Default</label><code>None</code>
		</p>
	</dd>
</dl>

