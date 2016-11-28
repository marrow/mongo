# encoding: utf-8

from __future__ import unicode_literals

import operator
from datetime import datetime

import pytest
from bson import ObjectId as oid

from marrow.mongo import Document, Field, Filter, Q
from marrow.mongo.field import Array, Embed, Number, ObjectId, String
from marrow.schema.compat import odict, py3, str, unicode


class Sample(Document):
	class Embedded(Document):
		name = String()
	
	generic = Field()
	field = String('field_name')
	number = Number('field_name', default=27)
	array = Array(Number(default=42), name='field_name')
	embed = Embed(Embedded)

mock_queryable = Sample.field

@pytest.fixture()
def S():
	class Stringy(Document):
		foo = String()
		bar = String()
		baz = String()
		diz = String()
	
	return Stringy

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
		assert isinstance(op, Filter)
		assert op.as_query == result
	
	def do_singleton(self, operator, query, result):
		op = operator(mock_queryable)
		assert isinstance(op, Filter)
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
		assert isinstance(op, Filter)
		
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
	
	def test_non_array_passthrough(self):
		with pytest.raises(TypeError):
			Sample.generic['foo']
	
	def test_array_non_numeric(self):
		with pytest.raises(KeyError):
			Sample.array['bar']


class TestQueryableQueryableQueryable(object):
	def test_left_merge(self, S):
		a = (S.foo & S.bar)
		b = S.baz
		z = a & b
		
		assert z._field == a._field + [b]
	
	def test_right_merge(self, S):
		a = S.foo
		b = (S.baz & S.diz)
		z = a & b
		
		assert z._field == [a] + b._field
	
	def test_twin_merge(self, S):
		a = (S.foo & S.bar)
		b = (S.baz & S.diz)
		z = a & b
		
		assert z._field == a._field + b._field
	


class TestQueryableFieldCombinations(object):
	@pytest.fixture()
	def T(self):
		class Thread(Document):
			class Reply(Document):
				id = ObjectId()
			
			id = ObjectId()
			reply = Embed(Reply)
		
		return Thread
	
	@pytest.fixture()
	def E(self):
		class Embeds(Document):
			class Embedded(Document):
				field = String()
			
			foo = Embed(Embedded)
			bar = Embed(Embedded)
		
		return Embeds
	
	@pytest.fixture()
	def A(self):
		class Arrays(Document):
			foo = Array(String())
			bar = Array(String())
		
		return Arrays
	
	def test_forum_example(self, T):
		comb = T.id | T.reply.id
		assert repr(comb) == "Q(Thread, '$or', [Q(Thread, 'id', ObjectId('id')), Q(Thread, 'reply.id', ObjectId('id'))])"
		
		q = comb.range(datetime(2016, 1, 1), datetime(2017, 1, 1))
		
		assert q.operations['$or']
		
		assert q.operations['$or'][0]['id']['$gte'] == q.operations['$or'][1]['reply.id']['$gte']
		assert q.operations['$or'][0]['id']['$lt'] == q.operations['$or'][1]['reply.id']['$lt']
	
	def test_equality_op(self, T):
		comb = T.id & T.reply.id
		v = oid()
		q = comb == v
		
		assert q.operations['id'] == v
		assert q.operations['reply.id'] == v
	
	def test_basic_op(self, T):
		comb = T.id & T.reply.id
		v = oid()
		q = comb > v
		
		assert q.operations['id']['$gt'] == v
		assert q.operations['reply.id']['$gt'] == v
	
	def test_iterable_op(self, T):
		comb = T.id & T.reply.id
		v = oid()
		q = comb.any([v])
		
		assert q.operations['id']['$in'] == [v]
		assert q.operations['reply.id']['$in'] == [v]
	
	def test_re_op(self, S):
		comb = S.foo & S.bar
		q = comb.re('^', 'foo', '$')
		
		assert q.operations['foo']['$re'] == '^foo$'
		assert q.operations['bar']['$re'] == '^foo$'
	
	def test_match_op(self, E):
		comb = E.foo & E.bar
		v = {'foo': 'bar'}
		q = comb.match(v)
		
		assert q['foo']['$elemMatch'] == v
		assert q['bar']['$elemMatch'] == v
	
	def test_size_op(self, A):
		comb = A.foo & A.bar
		q = comb.size(27)
		
		assert q['foo']['$size'] == 27
		assert q['bar']['$size'] == 27
	
	def test_neg_op(self, S):
		comb = S.foo & S.bar
		q = -comb
		
		assert q['foo']['$exists'] == False
		assert q['bar']['$exists'] == False
	
	def test_pos_op(self, S):
		comb = S.foo & S.bar
		q = +comb
		
		assert q['foo']['$exists'] == True
		assert q['bar']['$exists'] == True
	
	def test_type_op(self, S):
		comb = S.foo & S.bar
		q = comb.of_type()
		
		assert q['foo']['$type'] == 'string'
		assert q['bar']['$type'] == 'string'
	
	def test_bad_combination(self, T):
		with pytest.raises(TypeError):
			assert T.id & 27
	
	def test_combination_attribute_access_fails(self, T):
		with pytest.raises(AttributeError):
			(T.id | T.reply.id).foo
	
	def test_combination_item_access_fails(self, T):
		with pytest.raises(KeyError):
			(T.id | T.reply.id)[27]
	
	def test_array_match_fails(self, T):
		with pytest.raises(TypeError):
			(T.id | T.reply.id).S
	
	def test_inversion_fails(self, T):
		with pytest.raises(TypeError):
			~(T.id ^ T.reply.id)
