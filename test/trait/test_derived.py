# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo.trait import Derived


class TestDerived(object):
	class Sample(Derived):
		pass
	
	def test_reference(self):
		inst = self.Sample()
		assert inst['_cls'] == 'test_derived:TestDerived.Sample'
	
	def test_repr(self):
		inst = self.Sample()
		assert repr(inst).startswith('test_derived:TestDerived.Sample')
	
	def test_load(self):
		inst = Derived.from_mongo({'_cls': 'test_derived:TestDerived.Sample'})
		assert isinstance(inst, self.Sample)
	
	def test_index(self):
		assert '_cls' in self.Sample.__indexes__
