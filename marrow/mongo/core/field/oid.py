from bson import ObjectId as OID
from datetime import datetime, timedelta
from typing import MutableMapping

from .base import Field
from ....schema import Attribute


class ObjectId(Field):
	__foreign__ = 'objectId'
	__disallowed_operators__ = {'#array'}
	
	default = Attribute()
	
	def __fixup__(self, document):
		super(ObjectId, self).__fixup__(document)
		
		try:  # Assign a default if one has not been given.
			self.default
		except AttributeError:
			if self.__name__ == '_id':  # But only if we're actually the primary key.
				self.default = lambda: OID()  # pylint:disable=unnecessary-lambda
	
	def to_foreign(self, obj, name, value):  # pylint:disable=unused-argument
		if isinstance(value, OID):
			return value
		
		if isinstance(value, datetime):
			return OID.from_datetime(value)
		
		if isinstance(value, timedelta):
			return OID.from_datetime(datetime.utcnow() + value)
		
		if isinstance(value, MutableMapping) and '_id' in value:
			return OID(value['_id'])
		
		return OID(str(value))
