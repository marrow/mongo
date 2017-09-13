# encoding: utf-8

from __future__ import unicode_literals

from binascii import hexlify
from bson import ObjectId as OID, DBRef
from datetime import timedelta
from os import getenv, getpid

from ....package.canonical import name
from ... import Document, Index, utcnow
from ...field import Date, String, Embed, Reference, Integer, ObjectId
from ...trait import Queryable
from ...util.capped import tail


log = __import__('logging').getLogger(__name__)


try:
	TimeoutError = TimeoutError
except:
	class TimeoutError(Exception):
		pass


# We default to the same algorithm PyMongo uses to generate hardware and process ID portions of ObjectIds.
def _identifier():
	return getenv('INSTANCE_ID', '{:06x}{:04x}'.format(
			int(hexlify(OID._machine_bytes), 16),
			getpid() % 0xFFFF,
		))


class Lockable(Queryable):
	"""A trait describing a document with a mutex (mutual exclusion) lock.
	
	You may explicitly call the acquire and release methods yourself:
	
		try:
			lockable_instance.acquire()
		except lockable_instance.Locked:
			... # Failure scenario.
		else:
			try:
				... # Critical section.
			
			finally:
				try:
					lockable_instance.release()
				except lockable_instance.Locked:
					... # Failure scenario.
	
	You can use instances utilizing this trait as context managers where the lock will be released in the event of an
	exception, without additional code on your part. For example:
	
		try:
			with lockable_instance:
				... # Critical section.
		
		except lockable_instance.Locked:
			... # Failure scenario.
	
	General locking is accomplished through atomic compare-and-swap, also referred to as "update if not different". We
	rely on the fact that MongoDB database operations are serilized in the operation log. If there is a dogpile on the
	lock, the first operation reaching the log will "win" and the compare operations on the subsequent attempts will
	prevent further modification.
	
	Awaiting locks requires that a Queue collection be defined, to be used for pushing messages. There are use-cases
	involving a queue per collection, a shared application queue, or even access of such queues on a different
	connection. To avoid bad assumptions on our part, it's easy (if possibly a little strange) to define your own:
	
		class Thing(Lockable):
			__collection__ = 'things'
			
			class Queue(Lockable.Queue):
				__collection__ = 'locks'
				__capped__ = 16 * 1024 * 1024  # 16 MiB
	
	Class closures are used to customize behaviours; you can, of course, just assign an external class to the Queue
	attribute if you wish. It should still subclass Lockable.Queue or must otherwise provide the same field
	attributes.
	
	Locks are held for a specific duration after acquisition. If the lock hasn't been prolonged before the locking
	period expires, the lock will be automatically freed on the next attempt to acquire it.
	"""
	
	lock = Embed('.Lock', default=None)
	
	class Locked(Exception):
		"""An exception raised when unable to acquire a lock."""
		
		def __init__(self, message, lock=None, *args, **kw):
			if lock:
				args = tuple(args) + tuple(args)
			
			super(self.__class__, self).__init__(message, *args, **kw)
			
			self.message = message
			self.lock = lock  # Implementation note: optional to not break pickling serialization.
	
	class Queue(Queryable):
		"""A prototype for a capped collection tracking lock releases."""
		
		id = ObjectId('_id', positional=False)
		mutex = Reference(concrete=True)
		event = String(choices={'acquired', 'prolonged', 'released', 'expired'})
	
	class Lock(Document):
		__period__ = timedelta(minutes=1)
		
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
			
			if document.Queue.__collection__:
				document.Queue(document, 'acquired').insert_one()
			
			if __debug__:  # pragma: no cover
				expires = self.expires
				reference = DBRef(document.__collection__, document.id)
				log.debug("Acquired new lock on {!r} expiring {}.".format(document, expires.isoformat()), extra={
					'agent': self.instance, 'expires': expires, 'mutex': reference, 'forced': forced})
		
		def prolonged(self, document):
			"""A callback triggered in the event this this mutex is prolonged."""
			
			if document.Queue.__collection__:
				document.Queue(document, 'prolonged').insert_one()
			
			if __debug__:  # pragma: no cover
				expires = self.expires
				reference = DBRef(document.__collection__, document.id)
				log.debug("Prolonged lock held on {!r} until {}.".format(document, expires.isoformat()), extra={
					'agent': self.instance, 'expires': expires, 'mutex': reference})
		
		def released(self, document, forced=False):
			"""A callback triggered in the event this mutex is released."""
			
			if document.Queue.__collection__:
				document.Queue(document, 'released').insert_one()
			
			if __debug__:  # pragma: no cover
				reference = DBRef(document.__collection__, document.id)
				log.debug("Released lock held on {!r}.".format(document), extra={
					'agent': self.instance, 'mutex': reference, 'forced': forced})
		
		def expired(self, document):
			"""A callback triggered in the event this record's lock has been expired."""
			
			if document.Queue.__collection__:
				document.Queue(document, 'expired').insert_one()
			
			if __debug__:  # pragma: no cover
				expires = self.expires
				reference = DBRef(document.__collection__, document.id)
				log.debug("Expired stale lock on {!r}.".format(document, expires.isoformat()), extra={
					'agent': self.instance, 'expires': expires, 'mutex': reference})
	
	def wait(self, timeout):
		D = self.Queue
		collection = D.get_collection()
		
		expect = DBRef(self.__collection__, self.id)
		
		for event in tail(collection, {}, timeout=timeout, aggregate=True):
			if ~D.mutex not in event or event[~D.mutex] != expect:
				continue
			
			if event[~D.event] == 'released':
				break
		
		else:
			raise TimeoutError("Mutex lock not released in time.")
	
	def acquire(self, timeout=0, force=False):
		"""Attempt to acquire an exclusive lock on this record.
		
		If a timeout is given (in seconds) then the acquire call will block for up to that much time attempting to
		acquire the lock. If the lock can not be acquired (either because it is already set or we time out) a Locked
		exception will be raised.
		"""
		
		if timeout and not (self.Queue.__collection__ and self.Queue.__capped__):
			raise NotImplementedError(name(self.__class__) + ".Queue has not been prepared.")
		
		D = self.__class__
		collection = self.get_collection()
		identity = self.Lock()
		
		if force:
			query = D.id == self
		
		else:
			query = D.lock == None
			query |= D.lock.instance == identity.instance
			query |= D.lock.time < (identity.time - identity.__period__)
			query &= D.id == self
		
		previous = collection.find_one_and_update(query, {'$set': {~D.lock: identity}}, {~D.lock: True})
		
		if previous is None:
			if timeout:
				try:
					self.wait(timeout)
				except TimeoutError:
					pass
				
				return self.acquire()
			
			lock = getattr(self.find_one(self, projection={~D.lock: True}), 'lock', None)
			raise self.Locked("Unable to acquire lock.", lock)
		
		if not force and ~D.lock in previous:
			previous = self.Lock.from_mongo(previous.get(~D.lock))
			
			if previous:
				if previous.expires < identity.time:
					previous.expired(self)
				
				if previous.instance != identity.instance:  # Dont re-broadcast acquisition of an already-held lock.
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
		query &= D.lock.time >= (identity.time - identity.__period__)
		
		previous = collection.find_one_and_update(query, {'$set': {~D.lock.time: identity.time}}, {~D.lock: True})
		
		if previous is None:
			lock = getattr(self.find_one(self, projection={~D.lock: True}), 'lock', None)
			
			if lock and lock.expires <= identity.time:
				lock.expired(self)
			
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
		
		previous = collection.find_one_and_update(query, {'$unset': {~D.lock: True}}, {~D.lock: True})
		
		if previous is None:
			lock = getattr(self.find_one(self, projection={~D.lock: True}), 'lock', None)
			raise self.Locked("Unable to release lock.", lock)
		
		lock = self.Lock.from_mongo(previous[~D.lock])
		
		if lock and lock.expires <= identity.time:
			lock.expired(self)
		
		identity.released(self, force)
	
	def __enter__(self):
		"""Lockable documents may be used as a context manager to naturally acquire and free the lock."""
		
		result = self.acquire()
		
		self.lock = result
		
		return result
	
	def __exit__(self, exc_type, exc_value, traceback):
		try:
			self.release()
		
		except self.Locked as e:
			if e.lock is not None:
				reference = DBRef(self.__collection__, self.id)
				log.critical("Encountered error attempting to release mutex lock.", exc_info=True, extra={
					'agent': self.lock.instance, 'expires': self.lock.expires, 'mutex': reference})
		
		else:
			self.lock = None
