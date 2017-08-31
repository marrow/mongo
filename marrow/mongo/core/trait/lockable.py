# encoding: utf-8

from binascii import hexlify
from bson import ObjectId as OID, DBRef
from datetime import timedelta
from os import getenv, getpid

from ... import Document, Index, utcnow
from ...document import MappedPluginReference, Company
from ...field import Date, String
from ...trait import Queryable


log = __import__('logging').getLogger(__name__)


# We default to the same algorithm PyMongo uses to generate hardware and process ID portions of ObjectIds.
_identifier = getenv('INSTANCE_ID', '{:06x}{:04x}'.format(
		int(hexlify(OID._machine_bytes, 16)),
		getpid() % 0xFFFF,
	))


class Lockable(Queryable):
	"""A trait describing a document with a mutex (mutual exclusion) lock.
	
	You may explicitly call the acquire and release methods yourself:
	
		try:
			lockable_instance.acquire()
		except lockable_instance.Locked:
			... # Failure scenario.
		
		... # Critical section.
		
		try:
			lockable_instance.release()
		except lockable_instance.Locked:
			... # Failure scenario.
	
	You can use instances utilizing this trait as context managers, where the lock will be released even in the event
	of an exception, without additional code on your part. For example:
	
		try:
			with lockable_instance:
				... # Critical section.
		except lockable_instance.Locked:
			... # Failure scenario.
	
	The locking process is accomplished in two distinct parts. First, there is the object (and collection) the lock is
	defined for. The lock is acquired and released using atomic MongoDB updates. On releases processes waiting for a
	held lock are notified using a shadow "capped collection" utilized just for this purpose. This allows waiting for
	a mutex to be released to be a push notification, rather than polling process.
	
	Locks are held for a specific duration after acquisition. If the lock hasn't been prolonged before the locking
	period expires, the lock will be automatically freed on the next attempt to acquire it.
	"""
	
	lock = Embed('.Lock', default=None)
	
	class Locked(Exception):
		"""Raised when unable to acquire the lock."""
		pass
	
	class Lock(Document):
		period = timedelta(minutes=1)
		
		time = Date(default=utcnow, assign=True)
		instance = String(default=_identifier, assign=True)
		timeouts = Integer(default=0, assign=True)
		
		@property
		def expires(self):
			"""Return the expiry time of the current mutex lease."""
			
			return self.time + self.__period__
		
		@property
		def failures(self):
			"""The number of consecutive failures to release.
			
			Calculated as the stored number of timeouts may not account for a current failure; it is updated on the
			next attempt to acquire.
			"""
			
			return self.timeouts + int(self.expires <= utcnow())
		
		def acquired(self, document, forced=False):
			"""A callback triggered in the event this mutex is acquired."""
			
			if __debug__:
				expires = self.expires
				reference = DBRef(document.__collection__, document.id)
				log.debug("Acquired new lock on {!r} expiring {}.".format(document, expires.isoformat()), extra={
					'agent': self.instance, 'expires': expires, 'mutex': reference, 'forced': forced})
		
		def prolonged(self, document):
			"""A callback triggered in the event this this mutex is prolonged."""
			
			if __debug__:
				expires = self.expires
				reference = DBRef(document.__collection__, document.id)
				log.debug("Prolonged lock held on {!r} until {}.".format(document, expires.isoformat()), extra={
					'agent': self.instance, 'expires': expires, 'mutex': reference})
		
		def released(self, document, forced=False):
			"""A callback triggered in the event this mutex is released."""
			
			if __debug__:
				reference = DBRef(document.__collection__, document.id)
				log.debug("Released lock held on {!r}.".format(document), extra={
					'agent': self.instance, 'mutex': reference, 'forced': forced})
		
		def expired(self, document):
			"""A callback triggered in the event this record's lock has been expired, prior to re-locking."""
			
			if __debug__:
				expires = self.expires
				reference = DBRef(document.__collection__, document.id)
				log.debug("Expired stale lock on {!r}.".format(document, expires.isoformat()), extra={
					'agent': self.instance, 'expires': expires, 'mutex': reference})
	
	def acquire(self, await=0, force=False):
		"""Attempt to acquire an exclusive lock on this record.
		
		TBD: If an await time is given (in seconds) then the acquire call will block for up to that much time
		attempting to get the lock. If the lock can not be acquired (either because it is already set or we time out)
		a Locked exception will be raised.
		"""
		
		if await:
			raise NotImplementedError()
		
		D = self.__class__
		collection = self.get_collection()
		identity = self.Lock()
		
		if force:
			query = D.id == self
		
		else:
			query = D.lock == None
			query |= D.lock.instance == identity.instance
			query |= D.lock.time < (identity.time - identity.period)
			query &= D.id == self
		
		previous = collection.find_one_and_update(query, {'$set': {~D.lock: identity}}, {~D.lock: True})
		
		if previous is None:
			lock = getattr(self.find_one(self, projection={~D.lock: True}), 'lock', None)
			raise self.Locked("Unable to acquire lock.", lock)
		
		if not force:
			previous = self.Lock.from_mongo(previous[~D.lock])
			
			if previous.expires < identity.time:
				previous.expired(self)
		
		identity.acquired(self, force)
		
		return identity
	
	def prolong(self):
		"""Prolong the working duration of an already held lock.
		
		Attempting to prolong a lock not already owned will result in a Locked exception.
		"""
		
		D = self.__class__
		collection = self.get_collection()
		identity = self.Lock()
		
		query = D.id == self
		query &= D.lock.instance == identity.instance
		query &= D.lock.time >= (identity.time - identity.period)
		
		previous = collection.find_one_and_update(query, {'$set': {~D.lock.time: identity.time}}, {~D.lock: True})
		
		if previous is None:
			lock = getattr(self.find_one(self, projection={~D.lock: True}), 'lock', None)
			
			if lock and lock.expires <= identity.time:
				previous.expired(self)
			
			raise self.Locked("Unable to prolong lock.", lock)
		
		identity.prolonged(self)
		
		return identity
	
	def release(self, force=False):
		"""Release an exclusive lock on this integration task.
		
		Unless forcing, if we are not the current owners of the lock a Locked exception will be raised.
		"""
		
		D = self.__class__
		collection = self.get_collection()
		identity = self.Lock()
		
		query = D.id == self
		
		if not force:
			query &= D.lock.instance == identity.instance
		
		previous = collection.find_one_and_update(query, {'$set': {~D.lock: None}}, {~D.lock: True})
		
		if previous is None:
			lock = getattr(self.find_one(self, projection={~D.lock: True}), 'lock', None)
			
			if lock and lock.expires <= identity.time:
				previous.expired(self)
			
			raise self.Locked("Unable to release lock.", lock)
		
		identity.released(self, force)
	
	def __enter__(self):
		"""Lockable documents may be used as a context manager to naturally acquire and free the lock."""
		
		self.lock = self.acquire()
		
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.lock = self.release()
