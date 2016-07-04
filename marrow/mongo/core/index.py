# encoding: utf-8

from weakref import proxy

from pymongo import ASCENDING, DESCENDING, GEO2D, GEOHAYSTACK, GEOSPHERE, HASHED, TEXT

from marrow.schema import Attribute


class Index(Attribute):
	PREFIX_MAP = {
			'': ASCENDING,
			'-': DESCENDING,
			'+': ASCENDING,
			'#': HASHED,
			'$': TEXT,
		}
	
	fields = Attribute(default=None)  # The set of fields and their sort orders.
	unique = Attribute(default=False)  # Is this index unique?
	background = Attribute(default=True)  # Create in the background by default?
	sparse = Attribute(default=False)  # Omit from the index documents that omit the field.
	expire = Attribute(default=None)  # Number of seconds after which to expire the record.
	partial = Attribute(default=None)  # A filter to use for partial indexing.
	
	# Marrow Schema Interfaces
	
	def __init__(self, *args, **kw):
		if args:
			kw['fields'] = self.process_fields(args)
		
		super(Index, self).__init__(**kw)
	
	def __fixup__(self, document):
		self.__document__ = proxy(document)
	
	# Data Descriptor Protocol
	
	def __get__(self, obj, cls=None):
		return self  # We're not really a field, so don't act like one.
	
	def __set__(self, obj, value):
		raise AttributeError()  # Can't be assigned to.
	
	# Our Index Protocol
	
	def process_fields(self, fields):
		result = []
		strip = ''.join(self.PREFIX_MAP)
		
		for field in fields:
			direction = self.PREFIX_MAP['']
			
			if field[0] in self.PREFIX_MAP:
				direction = self.PREFIX_MAP[field[0]]
				field = field.lstrip(strip)
			
			result.append((field, direction))
	
	def as_mongo(self):
		"""Perform the translation needed to return the arguments for `Collection.create_index`.
		
		This is where final field name resolution happens, via the reference we have to the containing document class.
		"""
		
		fields = [(self.__document__._get_mongo_name_for(i[0]), i[1]) for i in self.fields]
		
		options = dict(
				name = self.__name__,
				unique = self.unique,
				background = self.background,
				sparse = self.sparse,
				expireAfterSeconds = self.expire,
				partialFilterExpression = self.partial,
			)
		
		return fields, options

