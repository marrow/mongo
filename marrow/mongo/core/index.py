# encoding: utf-8

from weakref import proxy
from pymongo import ASCENDING, DESCENDING, GEO2D, GEOHAYSTACK, GEOSPHERE, HASHED, TEXT

from marrow.package.loader import traverse
from marrow.schema import Attribute

from ..util.compat import unicode


class Index(Attribute):
	PREFIX_MAP = {  # Prefix the name of your field with one of these to change the index type.
			'': ASCENDING,
			'-': DESCENDING,
			'+': ASCENDING,
			'@': GEO2D,
			'%': GEOHAYSTACK,
			'*': GEOSPHERE,
			'#': HASHED,
			'$': TEXT,
		}
	
	fields = Attribute(default=None)  # The set of fields and their sort orders.
	unique = Attribute(default=False)  # Is this index unique?
	background = Attribute(default=True)  # Create in the background by default?
	sparse = Attribute(default=False)  # Omit from the index documents that omit the field.
	expire = Attribute(default=None)  # Number of seconds after which to expire the record.
	partial = Attribute(default=None)  # A filter to use for partial indexing.
	bucket = Attribute(default=None)  # Bucket size for use with GeoHaystack indexes.
	min = Attribute(default=None)  # Minimum index key for use with a Geo2D index.
	max = Attribute(default=None)  # Maximum index key for use with a Geo2D index.
	
	def __init__(self, *args, **kw):
		if args:
			kw['fields'] = self.process_fields(args)
		
		super(Index, self).__init__(**kw)
	
	def __fixup__(self, document):
		"""Process the fact that we've been bound to a document; transform field references to DB field names."""
		
		self.fields = [(  # Transform field names.
				unicode(traverse(document, i[0], i[0])),  # Get the MongoDB field name.
				i[1]  # Preserve the field order.
			) for i in self.fields]
	
	def process_fields(self, fields):
		"""Process a list of simple string field definitions and assign their order based on prefix."""
		
		result = []
		strip = ''.join(self.PREFIX_MAP)
		
		for field in fields:
			direction = self.PREFIX_MAP['']
			
			if field[0] in self.PREFIX_MAP:
				direction = self.PREFIX_MAP[field[0]]
				field = field.lstrip(strip)
			
			result.append((field, direction))
		
		return result
	
	def create_index(self, collection, **kw):
		"""Perform the translation needed to return the arguments for `Collection.create_index`.
		
		This is where final field name resolution happens, via the reference we have to the containing document class.
		"""
		
		options = dict(
				name = self.__name__,
				unique = self.unique,
				background = self.background,
				sparse = self.sparse,
				expireAfterSeconds = self.expire,
				partialFilterExpression = self.partial,
				bucketSize = self.bucket,
				min = self.min,
				max = self.max,
			)
		options.update(kw)
		
		# Clear null options.
		for key in list(options):
			if options[key] is None:
				del options[key]
		
		return collection.create_index(self.fields, **options)
