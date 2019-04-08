from pprint import pprint

from marrow.mongo import Document
from marrow.mongo.field import Embed, ObjectId, String


class Sample(Document):
	class Nested(Document):
		name = String()
		reference = ObjectId()
	
	id = ObjectId('_id')
	nested = Embed('.Nested', assign=True)



pprint(Sample.id == None)
pprint(Sample.nested.name == "Alice")
