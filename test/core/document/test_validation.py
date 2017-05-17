# encoding: utf-8

from __future__ import unicode_literals

from marrow.mongo.field import Array, String
from marrow.mongo.trait import Collection


class StringDocument(Collection):
	optional = String()
	nonoptional = String(required=True)
	choose = String(choices=["Hello", "World"])


def test_string_document():
	validator = StringDocument.__validator__
	return
	
	assert validator == {
				'optional': {'$or': [{'$exists': 0}, {'$type': 'string'}]},
				'nonoptional': {'$type': 'string'},
				'choose':  {'$or': [{'$exists': 0}, {'$type': 'string', '$in': ['Hello', 'World']}]}
			}
