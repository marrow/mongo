# encoding: utf-8

from __future__ import unicode_literals

from datetime import timedelta
from time import sleep, time

import pytest

from marrow.mongo.core.trait.lockable import _identifier as us
from marrow.mongo.core.trait.lockable import TimeoutError
from marrow.mongo.trait import Lockable
from marrow.mongo.util import utcnow


class TestLockBehaviours(object):
	class Sample(Lockable):
		class Lock(Lockable.Lock):
			__period__ = timedelta(seconds=10)
	
	def test_expires(self):
		now = utcnow()
		inst = self.Sample.Lock(now)
		assert inst.expires == now + inst.__period__
	
	def test_failures_now(self):
		now = utcnow()
		inst = self.Sample.Lock(now)
		assert inst.failures == 0
	
	def test_failures_then(self):
		then = utcnow() - timedelta(days=30)
		inst = self.Sample.Lock(then)
		
		assert inst.failures == 1
	
	def test_failures_chain(self):
		then = utcnow() - timedelta(days=30)
		inst = self.Sample.Lock(then, timeouts=41)
		
		assert inst.failures == 42


class TestSimpleLockable(object):
	class Sample(Lockable):
		__collection__ = 'lockable'
		
		class Lock(Lockable.Lock):
			__period__ = timedelta(seconds=10)
			
			def expired(self, document):
				document.__dict__['did_expire'] = True
				
				super(self.__class__, self).expired(document)
	
	@pytest.fixture
	def sample(self, connection):
		db = connection.get_database()
		Sample = self.Sample.bind(db)
		
		try:
			Sample.create_collection()
		except:
			pass
		
		try:
			if Sample.Queue.__collection__:
				Sample.Queue.bind(db).create_collection()
				Sample.Queue().insert_one()
		except:
			pass
		
		instance = Sample()
		instance.insert_one()
		return instance
	
	def test_acquire(self, sample):
		lock = sample.acquire()
		
		sample.reload('lock')
		
		assert lock.instance is us
		assert sample.lock == lock
	
	def test_acquire_removed(self, sample):
		sample.delete_one()
		
		try:
			sample.acquire()
		
		except sample.Locked as e:
			assert e.lock is None
	
	def test_acquire_expired(self, sample):
		then = utcnow() - timedelta(days=30)
		sample.update_one(set__lock=sample.Lock(then, 'xyzzy'))
		
		sample.acquire()
		sample.reload('lock')
		
		assert sample.lock.instance == us
		assert sample.did_expire
	
	def test_acquire_twice(self, sample):
		lock = sample.acquire()
		
		try:
			sample.acquire()
		except sample.Locked as e:
			assert e.lock == lock
	
	def test_acquire_force(self, sample):
		lock = sample.acquire()
		
		sample.reload('lock')
		assert sample.lock == lock
		
		lock2 = sample.acquire(force=True)
		sample.reload('lock')
		
		assert sample.lock == lock2
	
	def test_acquire_wait(self, sample):
		sample.acquire()
		
		with pytest.raises(NotImplementedError):
			sample.acquire(10)
	
	def test_prolong_ours(self, sample):
		with sample as lock:
			sleep(2)
			lock2 = sample.prolong()
		
		assert lock.time < lock2.time
		assert lock.instance is lock2.instance is us
	
	def test_prolong_expired(self, sample):
		then = utcnow() - timedelta(days=30)
		lock = sample.Lock(then, us)
		sample.update_one(set__lock=lock)
		
		try:
			sample.prolong()
		except sample.Locked as e:
			assert e.lock == lock
			assert sample.did_expire
	
	def test_prolong_unlocked(self, sample):
		try:
			sample.prolong()
		except sample.Locked as e:
			assert e.lock is None
	
	def test_prolong_other(self, sample):
		sample.update_one(set__lock=sample.Lock(instance='xyzzy'))
		
		try:
			sample.prolong()
		
		except sample.Locked as e:
			assert e.lock.instance == 'xyzzy'
	
	def test_release_removed(self, sample):
		sample.acquire()
		
		sample.delete_one()
		
		try:
			sample.release()
		
		except sample.Locked as e:
			assert e.lock is None
	
	def test_relase_unlocked(self, sample):
		try:
			sample.release()
		
		except sample.Locked as e:
			assert e.lock is None
	
	def test_release_other(self, sample):
		sample.update_one(set__lock=sample.Lock(instance='xyzzy'))
		
		try:
			sample.release()
		
		except sample.Locked as e:
			assert e.lock.instance == 'xyzzy'
		
		sample.reload()
		assert sample.lock.instance == 'xyzzy'
	
	def test_release_forced(self, sample):
		sample.update_one(set__lock=sample.Lock(instance='xyzzy'))
		
		sample.release(True)
		
		sample.reload()
		assert sample.lock is None
	
	def test_release_expired(self, sample):
		then = utcnow() - timedelta(days=30)
		lock = sample.Lock(then, us)
		sample.update_one(set__lock=lock)
		
		try:
			sample.release()
		except sample.Locked as e:
			assert e.lock == lock
			assert sample.did_expire
	
	def test_context_manager(self, sample):
		assert sample.lock is None
		
		with sample as lock:
			assert sample.lock is lock
			sample.reload('lock')
			assert sample.lock == lock
		
		assert sample.lock is None
		sample.reload()
		assert sample.lock is None
	
	def test_context_failures(self, sample):
		with sample:
			sample.update_one(set__lock=sample.Lock(instance='xyzzy'))


class TestAwaitableLockable(TestSimpleLockable):
	class Sample(TestSimpleLockable.Sample):
		class Queue(Lockable.Queue):
			__collection__ = 'lockable_locks'
			__capped__ = 4 * 1024 * 1024
	
	def test_acquire_wait(self, sample):
		pass
	
	def test_wait_timeout(self, sample):
		start = time()
		
		with pytest.raises(TimeoutError):
			sample.wait(5)
		
		end = time()
		delta = end - start
		
		assert 2.5 < delta < 7.5
