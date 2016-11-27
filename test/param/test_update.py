# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo import Document, Field, U, Update
from marrow.mongo.field import Array, Number, String


class TestParametricUpdateConstructor(object):
	@pytest.fixture()
	def D(self):
		class Sample(Document):
			field = String()
			number = Number('other')
			array = Array(String())
		
		return Sample
	
	def test_set_default(self, D):
		q = U(D, field=27, number=42)
		assert isinstance(q, Update)
		assert q.operations == {'$set': {'field': '27', 'other': 42}}
	
	def test_dec(self, D):
		q = U(D, dec__number=42)
		assert isinstance(q, Update)
		assert q.operations == {'$inc': {'other': -42}}
	
	def test_alias(self, D):
		q = U(D, rename__field="name")
		assert isinstance(q, Update)
		assert q.operations == {'$rename': {'field': 'name'}}
	
	def test_bit(self, D):
		q = U(D, bit_xor__number=27)
		assert isinstance(q, Update)
		assert q.operations == {'$bit': {'other': {'xor': 27}}}
	
	def test_date(self, D):
		q = U(D, now__field=True)
		assert isinstance(q, Update)
		assert q.operations == {'$currentDate': {'field': True}}
	
	def test_timestamp(self, D):
		q = U(D, now__field='ts')
		assert isinstance(q, Update)
		assert q.operations == {'$currentDate': {'field': {'$type': 'timestamp'}}}
