# Getting Started

{% method -%}
Before you can progress very far you will need a connection to a MongoDB database.  See the [PyMongo documentation](http://api.mongodb.org/python/current) for more details on this. To get started quickly, the following snippet in a Python REPL shell will get you started as needed for the guide and tutorial sections of this manual.

{% sample lang="python" -%}
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost/test')
db = client.test
```
{% endmethod %}
