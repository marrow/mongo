# encoding: utf-8


from marrow.mongo.core import Document, Field
from marrow.mongo import ObjectId, String, Embed


class Sample(Document):
	class Nested(Document):
		name = String()
		reference = ObjectId()
	
	id = ObjectId('_id')
	nested = Embed(Nested, default=lambda: Nested(), assign=True)


from pprint import pprint

pprint(Sample.id == None)
pprint(Sample.nested.name == "Alice")
