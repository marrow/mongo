# encoding: utf-8

'''
from __future__ import unicode_literals

from marrow.mongo import Document
from marrow.mongo.core.field.complex import _HasKinds


class TestHasKinds(object):
	def test_singular(self):
		inst = _HasKinds(kind=1)
		assert list(inst.kinds) == [1]
	
	def test_iterable(self):
		inst = _HasKinds(kind=(1, 2))
		assert list(inst.kinds) == [1, 2]
	
	def test_positional(self):
		inst = _HasKinds(1, 2)
		assert list(inst.kinds) == [1, 2]
	
	def test_reference(self):
		inst = _HasKinds(kind='Document')
		assert list(inst.kinds) == [Document]
'''
