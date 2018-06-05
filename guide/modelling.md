# Document Modelling

The `Document` class heirarchy is organized to structure both data and the code manipulating it into clearly defined problems, with composable components focused on the principle of least concern. As such, the base class assumes very little; by itself it is a [`MutableMapping`](https://docs.python.org/3/library/collections.abc.html?highlight=abc#collections.abc.MutableMapping) abstract base class-compatible ordered dictionary proxy or wrapper, usable anywhere a mapping is usable. A notable difference is that the constructor only accepts arguments which have discrete fields associated with them.

There is no need for a specialized "dynamic" variant. Similarly, we have the philosophy that all documents are embeddable. Top-level documents in a collection, which expect an identifier, should utilize the specialization—_trait_—`Identified`.

{% method -%}
Begin by importing various components from the `marrow.mongo` package or one of the namespace packages for fields and traits, respectively.

{% sample lang="python" -%}
```python
from marrow.mongo import Index
from marrow.mongo.field import Array, Number, String, ObjectId
from marrow.mongo.trait import Queryable
```
{% endmethod %}
{% method -%}
To define a schema construct a `Document` subclass.  In this example, one to store information about user accounts. We utilize the `Queryable` subclass of `Document`, containing the majority of stateless _active record_ behaviour and provide (via `Identified`) an `id` field. All documents and traits you define must ultimately subclass `Document` in order to utilize the metaclass that makes the declarative mechanisms operate.

{% sample lang="python" -%}
```python
class Account(Queryable):
```
{% endmethod %}
{% method -%}
Initially we populate metadata. The first defines the name of the collection to use when _binding_ the class to a database, and is optional; you can bind it to a collection directly if you wish, or use it without binding at all. The second is used to specify a default validation level and generate a validation document (schema and/or constraints).

{% sample lang="python" -%}
```python
	__collection__ = 'accounts'
	__validate__ = 'strict'
	
```
{% endmethod %}
{% method -%}
Populate the class with a few different types of field by assigning `Field` instances as class attributes. Most accounts represent people, who have names. A simple string, with no constraints or transformation options given. Because no default value was given, any attempt to retrieve this attribute on an instance of `Account` prior to assigning one will raise an `AttributeError`, as a value for the field would not exist at all.

{% sample lang="python" -%}
```python
	name = String()
```
{% endmethod %}
{% method -%}
Fields missing from the document might be A-OK in some circumstances, but not all. We can mark our acount's `username` as required, resulting in the addition of a constraint when generating the validation document.

{% sample lang="python" -%}
```python
	username = String(required=True)
```
{% endmethod %}
{% method -%}
When utilizing default values you may choose to have the default value written immediately into the document. By utilizing the `assign` option the default value will be assigned to the instance immediately upon instantiation, unless passed to the constructor, resulting in the default value being present in the database. This armors records against potential future changes in the default value, if you do not wish such changes to propagate.

{% sample lang="python" -%}
```python
	locale = String(default='en-CA', assign=True)
```
{% endmethod %}
{% method -%}
We technically allow storage of any numeric value, either integer or floating point, for our user's age. To prevent explosions if an age is not given we define a default, though this default will not waste storage space in the database by being assigned.

{% sample lang="python" -%}
```python
	age = Number(default=None)
```
{% endmethod %}
{% method -%}
Now we define an array of free-form strings to utilize as tags. This is a complex field whose first argument is the type of value it contains and defaults to an empty version of the complex type it represents if assignment is enabled to eliminate the need for boilerplate code.

{% sample lang="python" -%}
```python
	tag = Array(String(), assign=True)
```
{% endmethod %}
{% method -%}
Even though `Account` inherits `Identified`, we don't want to gum up construction of new instances by allowing the ID to be defined positionally, so we adapt it. Adapted and redefined fields maintain their original order/position.

{% sample lang="python" -%}
```python
	id = Queryable.id.adapt(positional=False)
```
{% endmethod %}
{% method -%}
Lastly we define a unique index on the username to speed up any queries involving that field, and to enforce uniqueness. Because MongoDB's index capabilities are quite expressive, we do not define index features on fields themselves. It is generally a good idea to underscore-prefix non-field attributes. This helps keep fields distinct from non-fields in a visual way and implies they are "protected" or "private" as is customary in Python, though not enforced.

{% sample lang="python" -%}
```python
	
	_username = Index('username', unique=True)
```
{% endmethod %}

Now that we have a document defined we can move on to exploring how to interact with them.