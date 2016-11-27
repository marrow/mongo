# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo import Document, F, Field, Filter
from marrow.mongo.field import Array, Number


class TestParametricFilterConstructor(object):
	@pytest.fixture()
	def D(self):
		class Sample(Document):
			field = Field()
			number = Number()
			array = Array()
		
		return Sample
	
	def test_basic_equality_operator(self, D):
		q = F(D, field=27)
		assert isinstance(q, Filter)
		assert q == {'field': 27}
	
	def test_basic_gt_suffix_operator(self, D):
		q = F(D, field__gt=42)
		assert isinstance(q, Filter)
		assert q == {'field': {'$gt': 42}}
	
	def test_inverted_gt_suffix_operator(self, D):
		q = F(D, not__field__gt=42)
		assert isinstance(q, Filter)
		assert q == {'$not': {'field': {'$gt': 42}}}
	
	def test_deferred_method(self, D):
		q = F(D, field__size=27)
		assert isinstance(q, Filter)
		assert q == {'field': {'$size': 27}}
	
	def test_deferred_method_multiple_params(self, D):
		q = F(D, field__range=(27, 42))
		assert isinstance(q, Filter)
		assert q == {'field': {'$gte': 27, '$lt': 42}}
	
	def test_choice_operator(self, D):
		q = F(D, field__exists=True)
		assert isinstance(q, Filter)
		assert q == {'field': {'$exists': True}}
