# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo import Document, Field, S
from marrow.mongo.field import Array, Number


class TestParametricSortConstructor(object):
	@pytest.fixture()
	def D(self):
		class Sample(Document):
			field = Field()
			number = Number('other')
		
		return Sample
	
	def test_existing(self, D):
		q = S(D, ('field', 1))
		assert isinstance(q, list)
		assert q == [('field', 1)]
	
	def test_single(self, D):
		q = S(D, 'field')
		assert isinstance(q, list)
		assert q == [('field', 1)]
	
	def test_multiple(self, D):
		q = S(D, 'field', 'number')
		assert isinstance(q, list)
		assert q == [('field', 1), ('other', 1)]
	
	def test_sign(self, D):
		q = S(D, 'field', '-number')
		assert isinstance(q, list)
		assert q == [('field', 1), ('other', -1)]
