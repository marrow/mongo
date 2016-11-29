# Defining Documents

Documents are the records of MongoDB, stored in an efficient binary form called [BSON](http://bsonspec.org) allowing record manipulation that is cosmetically similar to JSON. In Python these are typically represented as dictionaries, Python's native mapping type.

{% method -%}
This package utilizes the [Marrow Schema](https://github.com/marrow/schema#readme) declarative schema toolkit and extends it to encompass MongoDB data storage concerns. Its documentation may assist you in understanding the processes involved in Marrow Mongo. Basically, you define data models by importing classes describing the various components of a collection, such as ``Document``, ``ObjectId``, or ``String``, then compose them into a declarative class model. For example, if you wanted to define a simple user account model, you would begin by importing various components from the `marrow.mongo` package.

{% sample lang="python" -%}
```python
from marrow.mongo import Index, Document
from marrow.mongo.field import ObjectId, String, Number, Array
```
{% endmethod %}

Let us define our own ``Document`` subclass:

{% label %}Python{% endlabel %}
```python
class Account(Document):
	username = String(required=True)
	name = String()
	locale = String(default='en-CA-u-tz-cator-cu-CAD', assign=True)
	age = Number()

	id = ObjectId('_id', assign=True)
	tag = Array(String(), default=lambda: [], assign=True)

	_username = Index('username', unique=True)
```

Breaking this chunk of code down:

```python
class Account(Document):
```

No surprises here, we subclass the `Document` class. This is required to utilize the metaclass that makes the declarative naming and order-preserving sequence generation work. We begin to define fields:

```python
username = String(required=True)
name = String()
locale = String(default='en-CA-u-tz-cator-cu-CAD', assign=True)
```

Introduced here is `required`, indicating that when generating the *validation document* for this document to ensure this field always has a value. This validation is not currently performed application-side. Also notable is the use of `assign` on a string field; this will assign the default value during instantiation. Then we have a different type of field:

```python
age = Number()
```

This allows storage of any numeric value, either integer or floating point. Now there is the record identifier:

```python
id = ObjectId('_id', assign=True)
```

Marrow Mongo does not assume your documents contain IDs; there is no separation internally between top-level documents and *embedded documents*, leaving the declaration of an ID up to you. You might not always wish to use an ObjectID, either; please see MongoDB's documentation for discussion of general modelling practices. The first positional parameter for most non-complex fields is the name of the MongoDB-side field. Underscores imply an attribute is "protected" in Python, so we remap it by assigning it to just `id`. The `assign` argument here ensures whenever a new `Account` is instantiated an ObjectID will be immediately generated and assigned.

Finally there is an array of tags:

```python
tag = Array(String(), default=lambda: [], assign=True)
```

This combines what we've been using so far into one field. An `Array` is a *complex field* (a container) and as such the types of values allowed to be contained therein may be defined positionally. (If you want to override the field's database-side name, pass in a `name` as a keyword argument.) A default is defined as an anonymous callback function which constructs a new list on each request. The default will be executed and the result assigned automatically during initialization as per `id` or `locale`.

Lastly we define a unique index on the username to speed up any queries involving that field:

```python
_username = Index('username', unique=True)
```
