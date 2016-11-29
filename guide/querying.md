# Querying Documents

Given the model defined in the [Documents](documents.md) section, a PyMongo collection object, and a record stored in the database we can retrieve it back out and get the result as an ``Account`` instance:

{% method -%}
Several things are going on here. First it's important to note that Marrow Mongo isn't making the query happen for you, and does not automatically cast dictionaries to `Document` subclasses when querying. The first line demonstrates the native approach to building *filter documents*, the first argument to `find` or `find_one`.

{% sample lang="python" -%}
```python
record = collection.find_one(Account.username == 'amcgregor')
record = Account.from_mongo(record)

print(record.name) # Alice Bevan-McGregor
```
{% endmethod %}

You can use standard Python comparison operators, bitwise operators, and several additional querying methods through class-level access to the defined fields. The result of one of these operations or method calls is a dictionary-like object that is the query. They may be combined through bitwise and (`&`) and bitwise or (`|`) operations, however due to Python's order of operations, individual field comparisons must be wrapped in parenthesis if combining.

Combining produces a new `Ops` instance, so it is possible to use these to pre-construct parts of queries prior to use. As a tip, it can save time (and visual clutter) to assign the document class to a short, single-character variable name to make repeated reference easier.
