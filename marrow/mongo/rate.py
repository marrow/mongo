# encoding: utf-8

"""Tools to implement rate limiting using MongoDB atomic operations."""





class RateLimit(object):
	__slots__ = ('collection', )
	
	def __init__(self, collection):
		self.collection = collection
	
	def find(self, query):
		raise NotImplementedError()
	
	def deduct(self, criteria):
		raise NotImplementedError()



class BasicRateLimit(RateLimit):
	"""Limit to X deductions per Y unit of time.
	
	This can be visualized as a bucket capable of holding X marbles that is completely refilled after Y minutes.
	
	It is recommended to enable the time-to-live (TTL) index using the "create_indexes" method in order to clean up
	old buckets automatically as well as create the indexes nessicary to optimize the queries this style of rate limit
	utilizes; this method is safe by default, creating the indexes only if needed, and in the background.
	"""
	
	__slots__ = ('collection', 'capactiy', 'schedule', 'base', 'floor')
	
	def __init__(self, collection, capacity, schedule, base=None, floor=True):
		"""Configure a basic rate limiter.
		
		The `collection` argument should be the literal pymongo collection object you wish to store limit data within,
		`capacity` should be an integer value representing the number of allowed deductions per period, and `schedule`
		should be a timedelta representing the time period to limit within. The additional optional agument `base`
		provides a way to make this rate limiter instance store additional data aginst the individual rate limit
		records and ensures it queries for those values when updating.  (It does this using an `$and` operation.)
		
		Periods are snapped to multiples after midnight, UTC.  I.e. if your period is one hour the bucket is refilled
		at midnight, 0100, 0200, etc, unless the `floor` argument is set to `False`, in which case missing buckets are
		created on demand and refill an hour after initial creation.
		"""
		super(BasicRateLimit, self).__init__(collection)
		
		self.capacity = capacity
		self.schedule = schedule
		self.base = base
		self.floor = floor
	
	def create_indexes(self, ttl=True, delay=0, background=True):
		"""Create appropriate indexes to support collection use as a rate limit pool.
		
		
		"""
		pass
	
	def find(self, query):
		pass

	def deduct(self, criteria, amount=1):
		pass
