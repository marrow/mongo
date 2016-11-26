# encoding: utf-8

from __future__ import unicode_literals

import pytest

from marrow.mongo import Document, F, Field
from marrow.mongo.query import Ops


class TestParametricFilterConstructor(object):
	@pytest.fixture()
	def D(self):
		class Sample(Document):
			field = Field()
			bar = Field()
		
		return Sample
	
	def test_basic_equality_operator(self, D):
		q = F(D, field=27)
		assert isinstance(q, Ops)
		assert q == {'field': 27}
	
	def test_basic_gt_suffix_operator(self, D):
		q = F(D, field__gt=42)
		assert isinstance(q, Ops)
		assert q == {'field': {'$gt': 42}}
	
	def test_inverted_gt_suffix_operator(self, D):
		q = F(D, not__field__gt=42)
		assert isinstance(q, Ops)
		assert q == {'$not': {'field': {'$gt': 42}}}
