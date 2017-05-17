# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo import Field, P
from marrow.mongo.field import Array, Number
from marrow.mongo.trait import Collection


class TestParametricProjectionConstructor(object):
	@pytest.fixture()
	def D(self):
		class Sample(Collection):
			field = Field(project=True)
			number = Number('other')
		
		return Sample
	
	def test_basic_inclusion(self, D):
		q = P(D, 'number')
		assert isinstance(q, dict)
		assert q == {'other': True}
	
	def test_explicit_inclusion(self, D):
		q = P(D, '+number')
		assert isinstance(q, dict)
		assert q == {'other': True}
	
	def test_basic_exclusion(self, D):
		q = P(D, '-number')
		assert isinstance(q, dict)
		assert q == {'field': True}
	
	def test_default_exclusion(self, D):
		q = P(D, '-field')
		assert isinstance(q, dict)
		assert q == {'_id': True}
