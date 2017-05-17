# encoding: utf-8

from __future__ import unicode_literals

from bson.binary import STANDARD
from bson.codec_options import CodecOptions
from bson.tz_util import utc
from pymongo.collection import Collection as PyMongoCollection
from pymongo.database import Database
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from ...trait import Identified


__all__ = ['Collection']


class Collection(Identified):
	"""Allow this Document class to be bound to a real MongoDB database and collection.
	
	This extracts all "active-record"-like patterns from basic Document classes, eliminates the need to declare as a
	sub-class of Identified (all top-level Collection objects are identified by default), and generally helps break
	things apart into discrete groups of logical tasks.
	
	Currently true Active Record pattern access is not supported, nor encouraged. This provides a shortcut, as
	mentioned above, and access to common collection-level activites in ways utilizing positional and parametric
	helpers. Not all collection manipulating methods are proxied here; only the ones benefitting from assistance
	from Marrow Mongo in terms of binding or index awareness.
	
	For other operations (such as `drop`, `reindex`, etc.) it is recommended to `get_collection()` and explicitly
	utilize the PyMongo API. This helps reduce the liklihood of a given interface breaking with changes to PyMongo,
	avoids clutter, and allows you to use some of these method names yourself.
	"""
	
	# Metadata Defaults
	
	# Collection Binding
	__bound__ = None  # Has this class been "attached" to a live MongoDB connection? If so, this is the collection.
	__collection__ = None  # The name of the collection to "attach to" using a call to `bind()`.
	__projection__ = None  # The set of fields used during projection, to identify fields which are not loaded.
	
	# Data Access Options
	# TODO: Attribute declaration and name allowance.
	__read_preference__ = ReadPreference.PRIMARY  # Default read preference to assign when binding.
	__read_concern__ = ReadConcern()  # Default read concern.
	__write_concern__ = WriteConcern(w=1)  # Default write concern.
	
	# Storage Options
	__capped__ = False  # The size of the capped collection to create in bytes.
	__capped_count__ = None  # The optional number of records to limit the capped collection to.
	__engine__ = None  # Override the default storage engine (and configuration) as a mapping of `{name: options}`.
	__collation__ = None  # A `pymongo.collation.Collation` object to control collation during creation.
	
	# Data Validation Options
	__validate__ = 'off'  # Control validation strictness: `off`, `strict`, or `moderate`. TODO: bool/None equiv.
	__validator__ = None  # The MongoDB Validation document matching these records.
	
	@classmethod
	def __attributed__(cls):
		"""Executed after each new subclass is constructed."""
		
		cls.__projection__ = cls._get_default_projection()
	
	# Data Access Binding
	
	@classmethod
	def bind(cls, target):
		"""Bind a copy of the collection to the class, modified per our class' settings.
		
		The given target (and eventual collection returned) must be safe within the context the document sublcass
		being bound is constructed within. E.g. at the module scope this binding must be thread-safe.
		"""
		
		if cls.__bound__ is not None:
			return cls
		
		cls.__bound__ = cls.get_collection(target)
		
		return cls
	
	# Collection Management
	
	@classmethod
	def get_collection(cls, target=None):
		"""Retrieve a properly configured collection object as configured by this document class.
		
		If given an existing collection, will instead call `collection.with_options`.
		
		http://api.mongodb.com/python/current/api/pymongo/database.html#pymongo.database.Database.get_collection
		"""
		
		if target is None:
			assert cls.__bound__ is not None, "Target required when document class not bound."
			return cls.__bound__
		
		if isinstance(target, PyMongoCollection):
			return target.with_options(**cls._collection_configuration())
		
		elif isinstance(target, Database):
			return target.get_collection(cls.__collection__, **cls._collection_configuration())
		
		raise TypeError("Can not retrieve collection from: " + repr(target))
	
	@classmethod
	def create_collection(cls, target=None, drop=False, indexes=True):
		"""Ensure the collection identified by this document class exists, creating it if not, also creating indexes.
		
		**Warning:** enabling the `recreate` option **will drop the collection, erasing all data within**.
		
		http://api.mongodb.com/python/current/api/pymongo/database.html#pymongo.database.Database.create_collection
		"""
		
		if target is None:
			assert cls.__bound__ is not None, "Target required when document class not bound."
			target = cls.__bound__
		
		if isinstance(target, PyMongoCollection):
			collection = target.name
			target = target.database
		elif isinstance(target, Database):
			collection = cls.__collection__
		else:
			raise TypeError("Can not retrieve database from: " + repr(target))
		
		if drop:
			target.drop_collection(collection)  # TODO: If drop fails, try just emptying?
		
		collection = target.create_collection(collection, **cls._collection_configuration(True))
		
		if indexes:
			cls.create_indexes(collection)
		
		return collection
	
	# Index Management
	
	@classmethod
	def create_indexes(cls, target=None, recreate=False):
		"""Iterate all known indexes and construct them.
		
		https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.create_indexes
		"""
		
		# TODO: Nested indexes.
		
		results = []
		collection = cls.get_collection(target)
		
		if recreate:
			collection.drop_indexes()
		
		for index in cls.__indexes__.values():
			results.append(index.create(collection))
		
		return results
	
	# Semi-Private Data Transformation
	
	@classmethod
	def _collection_configuration(cls, creation=False):
		config = {
				'codec_options': CodecOptions(
						document_class = cls.__store__,
						tz_aware = True,
						uuid_representation = STANDARD,
						tzinfo = utc,
					),
				'read_preference': cls.__read_preference__,
				'read_concern': cls.__read_concern__,
				'write_concern': cls.__write_concern__,
			}
		
		if not creation:
			return config
		
		if cls.__capped__:
			config['size'] = cls.__capped__
			config['capped'] = True
			
			if cls.__capped_count__:
				config['max'] = cls.__capped_count__
		
		if cls.__engine__:
			config['storageEngine'] = cls.__engine__
		
		if cls.__validate__ != 'off':
			config['validator'] = cls.__validator__
			config['validationLevel'] = 'strict' if cls.__validate__ is True else cls.__validate__
		
		if cls.__collation__ is not None:  # pragma: no cover
			config['collation'] = cls.__collation__
		
		return config
	
	@classmethod
	def _get_default_projection(cls):
		"""Construct the default projection document."""
		
		projected = []  # The fields explicitly requested for inclusion.
		neutral = []  # Fields returning neutral (None) status.
		omitted = False  # Have any fields been explicitly omitted?
		
		for name, field in cls.__fields__.items():
			if field.project is None:
				neutral.append(name)
			elif field.project:
				projected.append(name)
			else:
				omitted = True
		
		if not projected and not omitted:
			# No preferences specified.
			return None
			
		elif not projected and omitted:
			# No positive inclusions given, but negative ones were.
			projected = neutral
		
		return {field: True for field in projected}
