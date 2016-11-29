# Document Instances

With a document schema defined we can now begin populating data:

{% label %}Python REPL{% endlabel %}
```python
alice = Account('amcgregor', "Alice Bevan-McGregor", age=27)
print(alice.id) # Already has an ID.
print(alice.id.generation_time) # This even includes the creation time.
```
As can be seen above construction accepts positional and keyword parameters. Fields will be filled, positionally, in the order they were defined, unless otherwise adjusted using the `adjust_attribute_sequence` decorator.

Assuming a `pymongo` collection is accessible by the variable name `collection` we can construct our index:

```python
Account.create_indexes(collection)
```

There is no need to run this command more than once unless the collection is dropped.

Let's insert our record:

```python
result = collection.insert_one(alice)
assert result.acknowledged and result.inserted_id == alice.id
```

Yup, that's it. Instances of `Document` are directly usable in place of a dictionary argument to `pymongo` methods. We then validate that the document we wanted inserted was, in fact, inserted. Using an assert in this way, this validation will not be run in production code run with the `-O` option passed (or `PYTHONOPTIMIZE` environment variable set) in the invocation to Python.
