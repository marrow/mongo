# encoding: utf-8

import pytest

from marrow.mongo.util import UniversalMethod


class TestUM(object):
	class Sample(object):
		@UniversalMethod
		def method(cls):
			return "I'm the original: " + repr(cls)
		
		@method.instancemethod
		def method(self):
			return "I'm an instance: " + repr(self)
		
		@method.classmethod
		def method(cls):
			return "I'm the class: " + repr(cls)
	
	@pytest.fixture(scope='class')
	def sample(self):
		return self.Sample()
	
	def test_classmethod(self):
		result = self.Sample.method()
		assert 'class' in result
		assert 'Sample' in result
	
	def test_instancemethod(self, sample):
		result = sample.method()
		assert 'instance' in result
		assert 'Sample' in result
