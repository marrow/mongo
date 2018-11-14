# Alias

An `Alias` is a proxy to another field, potentially nested, within the same document.

Utilizing an `Alias` allows class-level querying and instance-level read access, write access under most conditions, as well as optional deprecation warning generation.

<dl>
	<dt><h5>Import</h5></dt><dd><p><code>from marrow.mongo.field import Alias</code></p></dd>
	<dt><h5>Inherits</h5></dt><dd><p><code>marrow.schema:<strong>Attribute</strong></code></p></dd>
	<dt><h5>Added</h5></dt><dd><p><code>&gt;=1.1.0</code> <a href="https://github.com/marrow/mongo/releases/tag/1.1.0">Oranir</a></p></dd>
</dl>


## Attributes

This pseudo-field **does not** inherit other field attributes.

<dl>
	<dt><h5><code>path</code></h5></dt><dd>
		<p>A string reference to another field in the same containing class. See the <a href="#usage">Usage</a> section below for the structure of these references.</p>
		<p><label>Required</label></p>
	</dd><dt><h5><code>deprecate</code></h5></dt><dd>
		<p>Used to determine if access should issue <code>DeprecationWarning</code> messages. If truthy, a warning will be raised, and if non-boolean the string value will be included in the message.</p>
		<p><label>Default</label><code>False</code></p>
		<p><label>Added</label><code>&gt;=1.1.2</code></p>
	</dd>
</dl>


## Usage

Instantiate and assign an instance of this class during construction of a new `Document` subclass, passing the attributes in as positional (in the order seen above) or keyword arguments. This pseudo-field utilizes the Marrow Package [`traverse`](https://github.com/marrow/package#4-resolving-object-references) utility to allow it to resolve a wide variety of attributes.

References to other fields may be:

* The string name of a sibling attribute.  
  <label>Example</label><code>'id'</code>

* The path to a descendant attribute of a sibling.  
  <label>Example</label><code>'address.city'</code>

* Or involving numeric array indexes.  
  <label>Example</label><code>'some_array.0'</code>

* Or involving dictionary key references.  
  <label>Example</label><code>'locale.en'</code>

Paths are strings comprised of dot-separated attribute names. The search beings at the containing document, consuming path elements as we go. Each path element is first attempted as an attribute and, failing that, will attempt dictionary access. If the path element is numeric, it will be utilized as an array index.

Accessing an `Alias` at the class level will resolve a Queryable for the target field, allowing filter document construction through comparison utilizing the `alias` name itself. On an instance access will retrieve or assign the value of the target field.


## Examples

#### Sibling Reference

{% method -%}
As it might not be natural to refer to the user's username everywhere as `id`, especially if dereferenced from a variable, you can use an `Alias` to provide a more contextual name for the identifier.

{% sample lang="python" -%}
```python
class User(Document):
	id = String('_id')
	username = Alias('id')


User.find_many(username__startswith="a")
```
{% endmethod %}


#### Descendant Attribute of a Sibling

{% method -%}
There are situations where elevating an embedded value can be useful to, for example, shorten frequent queries or variable references in templates.

{% sample lang="python" -%}
```python
class Package(Document):
	class Address(Document):
		city = String()
		...
	
	address = Embed(Address, assign=True)
	city = Alias('address.city')
```
{% endmethod %}


#### Numeric Array Index Reference

{% method -%}
If you're savvy and always insert the most recent message at the beginning of the unread messages array, you can easily and semantically access the latest message using an `Alias`.

{% sample lang="python" -%}
```python
class Conversation(Document):
	class Message(Document):
		id = ObjectId('_id')
		sender = Field()
		message = Field()
	
	messages = Array(Embed(Message), assign=True)
	latest = Alias('messages.0')
```
{% endmethod %}


#### Legacy Alternative Names / Deprecation

{% method -%}
Data modelling requirements change over time and there can be a lot of code referencing a given document attribute. Help identify where that access is coming from by marking old, deprecated attributes using `Alias` with an appropriate message.

<label>Added</label><code>&gt;=1.1.2</code>


{% sample lang="python" -%}
```python
class User(Document):
	id = String('_id')
	username = Alias('id',
		deprecate="Username is now primary key.")
```
{% endmethod %}


## See Also

* [`traverse`](https://github.com/marrow/package#4-resolving-object-references)
