# encoding: utf-8
# pragma: no cover

"""Note: experimental thingamabob."""

from __future__ import unicode_literals


__all__ = ['Model']

log = __import__('logging').getLogger(__name__)


class Model(object):
	"""Lazy access to MongoDB database collections via the WebCore request context.
	
	Assign instances of this lazy loader to your endpoint classes and make sure your endpoint class stores the request
	context as `self._ctx` as per convention.  For example:
		
		class Hello:
			_people = Model('people', cache='_people')
			
			def __init__(self, context):
				self._ctx = context
			
			def __call__(self, id):
				return "Hello " + self._people.find_one({'_id': ObjectId(id)})['name'] + "!"
	
	Because the WebCore dispatch process constructs new instances on each request, we can safely cache the result and
	overwrite the descriptor on the instance. (This is only possible because we do not provide a `__set__` descriptor
	method!)
	"""
	
	__slots__ = ('database', 'collection', 'model', 'cache')  # Instances of Model won't have a `dict` constructed.
	
	def __init__(self, collection, model=None, database='default', cache=None):
		"""Construct a new lazy loader for MongoDB collections.
		
		Pass in the string name of the collection as the first positional argument, optionally pass in a marrow.mongo
		document class to remember for later, and the name of the database connection to access may be passed as a
		keyword arguemnt appropriately called `database`.
		
		If you want to utilize the cache (to save on repeated calls) you'll need to pass in the name of the attribute
		you wish to assign to on the instance as `cache`.
		"""
		self.database = database
		self.collection = collection
		self.model = model
		self.cache = cache
	
	def resolve(self, context):
		"""Given a WebCore request context, load our named collection out of the appropriate database connection."""
		return context.db[self.database][self.collection]
	
	def __get__(self, instance, cls=None):
		"""Descriptor protocol getter."""
		if instance is None: return self  # Return ourselves directly if requested from the class we were assigned to.
		
		collection = self.resolve(instance._ctx)
		
		if self.cache:  # Assign the cached value if requested.
			setattr(instance, self.cache, collection)
		
		return collection
