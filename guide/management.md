# Guide

## Collection Management

`Document` subclasses utilizing the `Collection` trait (which `Queryable` inherits) gain class-level _active record_ behaviours. Additionally, `Collection` inherits `Identified` as well, providing an automatically generated ObjectId field named `id` which maps to the stored `_id` key. There is a fairly substantial number of [collection metadata and calculated properties](reference/trait/collection.md#metadata) available.

{% method -%}
Before much can be done, it will be necessary to get a reference to a MongoDB connection or database object. Begin by importing the client object from the `pymongo` package.

{% sample lang="python" -%}
```python
from pymongo import MongoClient
```
{% endmethod %}
{% method -%}
Then, open a connection to a MongoDB server, here, running locally. We can save some space by defining the database to utilize at the same time, and requesting a handle to the default database back without needing to refer to it by name a second time.

{% sample lang="python" -%}
```python
client = MongoClient('mongodb://localhost/test')
db = client.get_database()
```
{% endmethod %}
{% method -%}
Binding our `Account` class to a database will look up the collection name to use from the `__collection__` attribute. Alternatively you could bind directly to a specific collection. Either way, binding will automatically apply the metadata options for data access and validation and enable the `get_collection` method to provide you the correct, configured object.

{% sample lang="python" -%}
```python
Account.bind(db)
```
{% endmethod %}
{% method -%}
Two class methods are provided for collection management requiring awareness of our metadata: `create_collection` and `create_indexes`. Creating the collection will create any declared indexes automatically by default. For other collection-level management operations it is recommended to utilize `get_collection` and issue calls to the PyMongo API directly.

{% sample lang="python" -%}
```python
Account.create_collection()
```
{% endmethod %}

With the class bound you can now more easily interact with your documents in the collection.
