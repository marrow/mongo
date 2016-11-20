# encoding: utf-8

from __future__ import unicode_literals

import pytest
import operator
from collections import OrderedDict as odict

from marrow.mongo import Document, Field
from marrow.mongo.field import String, Number, Array, Embed
from marrow.mongo.query import Ops, Q
from marrow.mongo.util.compat import py3, str, unicode


class Sample(Document):
	class Embedded(Document):
		name = String()
	
	generic = Field()
	field = String('field_name')
	number = Number('field_name', default=27)
	array = Array(Number(default=42), name='field_name')
	embed = Embed(Embedded)

mock_queryable = Sample.field


class TestQueryable(object):  # TODO: Properly use pytest fixtures for this...
	operators = [
			(operator.lt, '$lt', 27, {'field_name': {'$lt': '27'}}),
			(operator.le, '$lte', 27, {'field_name': {'$lte': '27'}}),
			(operator.eq, '$eq', "hOI!", {'field_name': 'hOI!'}),
			(operator.ne, '$ne', "hOI!", {'field_name': {'$ne': 'hOI!'}}),
			(operator.ge, '$gte', 27, {'field_name': {'$gte': '27'}}),
			(operator.gt, '$gt', 27, {'field_name': {'$gt': '27'}}),
		]
	
	singletons = [
			(operator.neg, '$exists', {'field_name': {'$exists': 0}}),
			(operator.pos, '$exists', {'field_name': {'$exists': 1}}),
			(Q.of_type, '$type', {'field_name': {'$type': 'string'}}),
		]
	
	advanced = [
			(Q.any, '$in', [1, 2, 3], {'field_name': {'$in': ['1', '2', '3']}}),
			(Q.none, '$nin', [1, 2, 3], {'field_name': {'$nin': ['1', '2', '3']}}),
			(Q.all, '$all', [1, 2, 3], {'field_name': {'$all': [1, 2, 3]}}),
			(Q.match, '$elemMatch', {'name': "Bob"}, {'field_name': {'$elemMatch': {'name': 'Bob'}}}),
			(Q.size, '$size', 42, {'field_name': {'$size': 42}}),
			(Q.of_type, '$type', "double", {'field_name': {'$type': 'double'}}),
		]
	
	def test_attribute_access(self):
		assert Sample.number.default == 27
		assert Sample.array.default == 42
		assert Sample.embed.name.__name__ == 'name'
		
		with pytest.raises(AttributeError):
			Sample.number.asdfasdf
		
		with pytest.raises(AttributeError):
			Sample.embed.asdfadsf
	
	def test_repr(self):
		assert repr(mock_queryable) == "Q(Sample, 'field_name', String('field_name'))"
	
	def test_s(self):
		assert unicode(Sample.array.S) == 'field_name.$'
	
	def test_embedded(self):
		assert unicode(Sample.embed.name) == 'embed.name'
	
	def do_operator(self, operator, query, value, result, mock_queryable=mock_queryable):
		op = operator(mock_queryable, value)
		assert isinstance(op, Ops)
		assert op.as_query == result
	
	def do_singleton(self, operator, query, result):
		op = operator(mock_queryable)
		assert isinstance(op, Ops)
		assert op.as_query == result
	
	def test_operator_lt(self): self.do_operator(*self.operators[0])
	def test_operator_lte(self): self.do_operator(*self.operators[1])
	def test_operator_eq(self): self.do_operator(*self.operators[2])
	def test_operator_ne(self): self.do_operator(*self.operators[3])
	def test_operator_gte(self): self.do_operator(*self.operators[4])
	def test_operator_gt(self): self.do_operator(*self.operators[5])
	
	def test_operator_neg(self): self.do_singleton(*self.singletons[0])
	def test_operator_pos(self): self.do_singleton(*self.singletons[1])
	
	def test_operator_any(self): self.do_operator(*self.advanced[0])
	def test_operator_none(self): self.do_operator(*self.advanced[1])
	def test_operator_match(self): self.do_operator(*self.advanced[3])
	def test_operator_type(self): self.do_operator(*self.advanced[5])
	def test_operator_type_assumed(self): self.do_singleton(*self.singletons[2])
	
	def test_operator_range(self):
		op = Q.range(mock_queryable, 5, 11)
		assert isinstance(op, Ops)
		
		assert op.as_query == odict({'field_name': dict([('$gte', '5'), ('$lt', '11')])})
	
	def test_op_failure(self):
		with pytest.raises(NotImplementedError):
			self.do_operator(*self.advanced[2], mock_queryable=Sample.array)
		
		with pytest.raises(NotImplementedError):
			self.do_operator(*self.advanced[4])
		
		with pytest.raises(NotImplementedError):
			Sample.number.size(27)
	
	def test_operator_type_bare(self):
		assert Sample.generic.of_type().as_query == {}
	
	def test_operator_invert(self):
		assert unicode(Sample.generic) == ~Sample.generic == 'generic'
	
	def test_operator_re(self):
		result = Sample.field.re(r'^', 'foo', r'\.')
		assert result.as_query == {'field_name': {'$re': r'^foo\.'}}
	
	def test_operator_size(self):
		result = Sample.array.size(10)
		assert result.as_query == {'field_name': {'$size': 10}}
	
	def test_match_query(self):
		result = Sample.array.match(Sample.Embedded.name == "Alice")
		assert result.as_query == {'field_name': {'$elemMatch': {'name': "Alice"}}}
