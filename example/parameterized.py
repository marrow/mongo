# encoding: utf-8

from pymongo import MongoClient

from marrow.mongo import Document
from marrow.mongo.field import Field
from marrow.mongo.query.parameterized import F


class Bar(Document):
	name = Field()
	value = Field()


class Foo(Document):
	name = Field()
	age = Field()
	
	attribute = Bar


q1 = F(Foo, age__gt=30)  # {'age': {'$gt': 30}}
q2 = (Foo.age > 30)  # {'age': {'$gt': 30}}
q3 = F(Foo, not__age__gt=30)  # {'age': {'$not': {'$gt': 30}}}
q4 = F(Foo, attribute__name__exists=False)  # {'attribute.name': {'$exists': 1}}

db = MongoClient().test
coll = db.foo
coll.drop()

coll.insert_one(Foo("Alice", 27))
coll.insert_one(Foo("Bob", 42))

print(list(coll.find(q1)))
print(list(coll.find(q2.as_query)))
print(list(coll.find(q3)))
print(list(coll.find(q4)))
