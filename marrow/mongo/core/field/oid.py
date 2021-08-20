from typing import Union

from bson import ObjectId as OID, DBRef
from bson.errors import InvalidId
from collections.abc import MutableMapping
from datetime import datetime, timedelta

from .base import Field
from ....schema import Attribute


SuitableIdentifier = Union[OID,datetime,timedelta,MutableMapping,str,bytes]


class ObjectId(Field):
	__foreign__ = 'objectId'
	__disallowed_operators__ = {'#array'}
	__annotation__ = OID
	
	default: SuitableIdentifier = Attribute()
	
	def __fixup__(self, document):
		super(ObjectId, self).__fixup__(document)
		
		try:  # Assign a default if one has not been given.
			self.default
		except AttributeError:
			if self.__name__ == '_id':  # But only if we're actually the primary key.
				self.default = lambda: OID()  # pylint:disable=unnecessary-lambda
	
	def to_foreign(self, obj, name:str, value:SuitableIdentifier) -> OID:  # pylint:disable=unused-argument
		if isinstance(value, OID):
			return value
		
		if isinstance(value, DBRef):
			if value.collection != obj.__collection__:
				raise ValueError(f"{value!r} does not reference our collection: {obj.__collection__}")
			
			return value.id
		
		if isinstance(value, datetime):
			return OID.from_datetime(value)
		
		if isinstance(value, timedelta):
			return OID.from_datetime(datetime.utcnow() + value)
		
		if isinstance(value, MutableMapping) and '_id' in value:
			return OID(value['_id'])
		
		try:
			return OID(value)
		except InvalidId:
			pass
		
		raise ValueError(f"Invalid ObjectID value: {value}")
