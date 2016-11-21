from marrow.mongo import Document
from marrow.mongo.field import String, Array, Binary, ObjectId, Boolean, Date


class StringDocument(Document):
	optional = String()
	nonoptional = String(required=True)
	choose = String(choices=["Hello", "World"])


def test_string_document():
	validator = StringDocument.__validation__
	return
	
	assert validator == {
				'optional': {'$or': [{'$exists': 0}, {'$type': 'string'}]},
				'nonoptional': {'$type': 'string'},
				'choose':  {'$or': [{'$exists': 0}, {'$type': 'string', '$in': ['Hello', 'World']}]}
			}



class ArrayDocument(Document):
	values = Array(String())
