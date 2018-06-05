# Document Interaction

Binding the class is not strictly needed in order to interact with them. You can instantiate, manipulate, and utilize as a mapping without it. Binding does, however, allow you to easily save the result and fetch records back out.


#### Record Creation

{% method -%}
When constructing an instance you may pass field values positionally as well as by name. Fields will be filled, positionally, in the order they were defined, skipping fields whose `positional` predicate is falsy.

{% sample lang="python" -%}
```python
alice = Account("Alice Bevan-McGregor", 'amcgregor', age=27)
```
{% endmethod %}
{% method -%}
The record has not even been persisted to the database yet and it has an identifier. This would allow you to create a batch of records, possibly with relationships, that can be committed at once. A read-only calculated property is provided to pull a creation time from the record's ObjectId creation time.

{% sample lang="python" -%}
```python
print(alice.id)  # Already there.
print(alice.created)  # Creation time from ID.
```
{% endmethod %}
{% method -%}
We can now insert our record into the database. We can verify the operation (we pass the return value of the PyMongo API call back to you) by ensuring the server acknowledged the write and double-checking the record's inserted ID. This second step is for illustrative purposes and is not generally needed in the wild.

{% sample lang="python" -%}
```python
result = alice.insert_one()
assert result.acknowledged
assert result.inserted_id == alice.id
```
{% endmethod %}

Using an assertion in this way, this validation will not be run in production code executed with the `-O` option passed (or `PYTHONOPTIMIZE` environment variable set) in the invocation to Python.


#### Record Retrieval

With a record stored in the database we can now issue queries and expect some form of result.

{% method -%}
Retrieving a record by its identifier, is simplified.  As there's an oddly large amount of weird in this line, we'll break it down a bit.

A call to `find_one` accepts a few different argument specifications to more flexibly serve the needs of queries simple to complex. The most basic form, taking one positional parameter, is that of querying by ID. Because our ID field is an ObjectId, it's aware that documents might have one and will pull it from a document if one is supplied.

{% sample lang="python" -%}
```python
alice = Account.find_one(alice)  # Wait... what?

print(alice.name) # Alice Bevan-McGregor
```
{% endmethod %}

All of the following are equivalent to the first.

{% method -%}
You can explicitly pass in a PyMongo ObjectId, or even a string representation of one.

{% sample lang="python" -%}
```python
alice = Account.find_one(alice.id)
```
{% endmethod %}
{% method -%}
More complex queries can be built from comparisons directly against the fields, resulting in a `Filter` mapping. Again, ObjectId fields know how to be compared against documents which contain IDs. This comparison does not have to be inline, and you can pass in any mapping representing a MongoDB filter document if you wish.

{% sample lang="python" -%}
```python
alice = Account.find_one(Account.id == alice)
alice = Account.find_one(Account.id == alice.id)
```
{% endmethod %}
{% method -%}
Using parametric querying, you can potentially save some typing. Multiple keyword arguments are combined using "and" logic. Note that this does not support the ability to create "or" conditions. The default comparison operator if none is specified is `eq`. You can still specify it explicitly if you wish.

{% sample lang="python" -%}
```python
alice = Account.find_one(id=alice)
alice = Account.find_one(id=alice.id)
alice = Account.find_one(id__eq=alice)
alice = Account.find_one(id__eq=alice.id)
```
{% endmethod %}
{% method -%}
We can, of course, query on anything we wish and not just the ID. What happens when we try to load a record that does not exist, though?

{% sample lang="python" -%}
```python
eve = Account.find_one(username="eve")
print(eve)  # None, no record was found.
```
{% endmethod %}

You can use standard Python comparison operators, bitwise operators, and several additional querying methods through class-level access to the defined fields. The result of one of these operations or method calls is a dictionary-like object that is the query, an instance of `Filter`. These may be combined through bitwise and (`&`) and bitwise or (`|`) operations. Due to Python's order of operations individual field comparisons must be wrapped in parenthesis if combining inline.

It is entirely possible to save pre-constructed parts of queries for later use. It can save time (and visual clutter) to assign the document class to a short, single-character variable name to make repeated reference easier.
