# encoding: utf-8

from __future__ import unicode_literals

import pytest
import operator

from marrow.mongo.query import Op, Ops, Queryable
from marrow.mongo.core.util import py2, str


@pytest.fixture
def empty_ops(request):
	return Ops()


@pytest.fixture
def single_ops(request):
	return Ops({'roll': 27})



class MockQueryable(Queryable):
	__foreign__ = 'string'
	
	def __str__(self):
		return "field_name"
	
	__unicode__ = __str__
	
	class transformer(object):
		@classmethod
		def foreign(self, value, context=None):
			return value


mock_queryable = MockQueryable()


class TestOpsMapping(object):
	def test_getitem(self, empty_ops, single_ops):
		with pytest.raises(KeyError):
			empty_ops['roll']
		
		assert single_ops['roll'] == 27
	
	def test_setitem(self, empty_ops):
		assert repr(empty_ops) == "Ops([])"
		empty_ops['meaning'] = 42
		assert repr(empty_ops) == "Ops([('meaning', 42)])"
	
	def test_delitem(self, empty_ops, single_ops):
		with pytest.raises(KeyError):
			del empty_ops['roll']
		
		assert repr(single_ops) == "Ops([('roll', 27)])"
		del single_ops['roll']
		assert repr(single_ops) == "Ops([])"
	
	def test_length(self, empty_ops, single_ops):
		assert len(empty_ops) == 0
		assert len(single_ops) == 1
	
	def test_keys(self, empty_ops, single_ops):
		assert list(empty_ops.keys()) == []
		assert list(single_ops.keys()) == ['roll']
	
	def test_items(self, empty_ops, single_ops):
		assert list(empty_ops.items()) == []
		assert list(single_ops.items()) == [('roll', 27)]
	
	def test_values(self, empty_ops, single_ops):
		assert list(empty_ops.values()) == []
		assert list(single_ops.values()) == [27]
	
	def test_contains(self, single_ops):
		assert 'foo' not in single_ops
		assert 'roll' in single_ops
	
	def test_equality_inequality(self, empty_ops, single_ops):
		assert empty_ops == {}
		assert empty_ops != {'roll': 27}
		assert single_ops != {}
		assert single_ops == {'roll': 27}
	
	def test_get(self, single_ops):
		assert single_ops.get('foo') is None
		assert single_ops.get('foo', 42) == 42
		assert single_ops.get('roll') == 27
	
	def test_clear(self, single_ops):
		assert len(single_ops.operations) == 1
		single_ops.clear()
		assert len(single_ops.operations) == 0
	
	def test_pop(self, single_ops):
		assert len(single_ops.operations) == 1
		
		with pytest.raises(KeyError):
			single_ops.pop('foo')
		
		assert single_ops.pop('foo', 42) == 42
		assert len(single_ops.operations) == 1
		
		assert single_ops.pop('roll') == 27
		assert len(single_ops.operations) == 0
	
	def test_popitem(self, single_ops):
		assert len(single_ops.operations) == 1
		assert single_ops.popitem() == ('roll', 27)
		assert len(single_ops.operations) == 0
		
		with pytest.raises(KeyError):
			single_ops.popitem()
	
	def test_update(self, empty_ops, single_ops):
		assert len(empty_ops.operations) == 0
		empty_ops.update(name="Bob Dole")
		assert len(empty_ops.operations) == 1
		assert repr(empty_ops) == "Ops([('name', 'Bob Dole')])"
		
		assert len(single_ops.operations) == 1
		assert repr(single_ops) == "Ops([('roll', 27)])"
		single_ops.update([('name', "Bob Dole")])
		assert len(single_ops.operations) == 2
		assert repr(single_ops) in ("Ops([('roll', 27), ('name', 'Bob Dole')])", "Ops([('name', 'Bob Dole'), ('roll', 27)])")
	
	def test_setdefault(self, empty_ops):
		assert len(empty_ops.operations) == 0
		empty_ops.setdefault('fnord', 42)
		assert len(empty_ops.operations) == 1
		assert empty_ops.operations['fnord'] == 42
		empty_ops.setdefault('fnord', 27)
		assert len(empty_ops.operations) == 1
		assert empty_ops.operations['fnord'] == 42


class TestOperationBasics(object):
	def test_empty_equals(self):
		assert Op(value=27).as_query == 27
		assert repr(Op(value=27)) == "Op(27)"
		
		assert Op(None, 'eq', '42').as_query == "42"
		assert repr(Op(None, 'eq', '42')) == ("Op(u'42')" if py2 else "Op('42')")
	
	def test_key_exists(self):
		assert Op('field').as_query == {'field': {'$exists': 1}}
		assert repr(Op('field')) == ("Op({u'field': {u'$exists': 1}})" if py2 else "Op({'field': {'$exists': 1}})")
	
	def test_key_equals(self):
		assert Op('field', value=27).as_query == {'field': 27}
		assert repr(Op('field', value=27)) == ("Op({u'field': 27})" if py2 else "Op({'field': 27})")
		
		assert Op('field', 'eq', '42').as_query == {'field': '42'}
		assert repr(Op('field', 'eq', '42')) == ("Op({u'field': u'42'})" if py2 else "Op({'field': '42'})")
	
	def test_bare_operation(self):
		assert Op(operation='operation').as_query == {'$operation': None}
	
	def test_fielded_operation(self):
		assert Op('field', 'operation', 'value').as_query == {'field': {'$operation': 'value'}}
	
	def test_clone(self):
		op1 = Op()
		assert repr(op1) == "Op(None)"
		
		op2 = op1.clone(value=27)
		assert repr(op2) == "Op(27)"
		
		op3 = op2.clone(field='field')
		assert repr(op3) == "Op({u'field': 27})" if py2 else "Op({'field': 27})"
		
		assert op1 is not op2
		assert op2 is not op3


class TestOperationCombination(object):
	def test_simple_and_merge(self):
		op1 = Op('a', value=27)
		op2 = Op('b', value=42)
		
		assert op1.as_query == {'a': 27}
		assert op2.as_query == {'b': 42}
		
		comb = op1 & op2
		
		assert repr(comb) == "Ops([('a', 27), ('b', 42)])"
		
		assert isinstance(comb, Ops)
		assert comb.as_query == {'a': 27, 'b': 42}
	
	def test_simple_and_merge_operations(self):
		op1 = Op('a', 'op', 27)
		op2 = Op('b', 'op', 42)
		
		assert op1.as_query == {'a': {'$op': 27}}
		assert op2.as_query == {'b': {'$op': 42}}
		
		comb = op1 & op2
		
		assert isinstance(comb, Ops)
		assert comb.as_query == {'a': {'$op': 27}, 'b': {'$op': 42}}
	
	def test_complex_and_operation(self):
		comb = Op(value={'a': 27}) & Op(value={'b': 42})
		
		assert isinstance(comb, Op)
		assert comb.as_query == {'$and': [{'a': 27}, {'b': 42}]}
	
	def test_or_operation(self):
		op1 = Op('a', value=27)
		op2 = Op('b', value=42)
		
		assert op1.as_query == {'a': 27}
		assert op2.as_query == {'b': 42}
		
		comb = op1 | op2
		
		assert isinstance(comb, Op)
		assert comb.as_query == {'$or': [{'a': 27}, {'b': 42}]}
	
	def test_simple_inversion(self):
		op = Op('a', value=27)
		
		assert op.as_query == {'a': 27}
		assert (~op).as_query == {'$not': {'a': 27}}


class TestOperationsCombination(object):
	def test_operations_and_with_operation(self):
		comb = Ops({'roll': 27}) & Op('foo', value=42)
		assert comb.as_query == {'roll': 27, 'foo': 42}
	
	def test_operations_and_clean_merge(self):
		comb = Ops({'roll': 27}) & Ops({'foo': 42})
		assert comb.as_query == {'roll': 27, 'foo': 42}
	
	def test_operations_and_operator_overlap(self):
		comb = Ops({'roll': {'$gte': 27}}) & Ops({'roll': {'$lte': 42}})
		assert comb.as_query == {'roll': {'$gte': 27, '$lte': 42}}
	
	def test_paradoxical_condition(self):
		comb = Ops({'roll': 27}) & Ops({'roll': {'$lte': 42}})
		assert comb.as_query == {'roll': {'$eq': 27, '$lte': 42}}
		
		comb = Ops({'roll': {'$gte': 27}}) & Ops({'roll': 42})
		assert list(comb.as_query['roll'].items()) in ([('$gte', 27), ('$eq', 42)], [('$eq', 42), ('$gte', 27)])
	
	def test_operations_or_with_operation(self):
		comb = Ops({'roll': 27}) | Op('foo', value=42)
		assert comb.as_query == {'$or': [{'roll': 27}, {'foo': 42}]}
	
	def test_operations_or_clean_merge(self):
		comb = Ops({'roll': 27}) | Ops({'foo': 42})
		assert comb.as_query == {'$or': [{'roll': 27}, {'foo': 42}]}
		
		comb = comb | Ops({'bar': 'baz'})
		assert comb.as_query == {'$or': [{'roll': 27}, {'foo': 42}, {'bar': 'baz'}]}


class TestQueryable(object):
	operators = [
			(operator.lt, '$lt', 27, {'field_name': {'$lt': 27}}),
			(operator.le, '$lte', 27, {'field_name': {'$lte': 27}}),
			(operator.eq, '$eq', "hOI!", {'field_name': 'hOI!'}),
			(operator.ne, '$ne', "hOI!", {'field_name': {'$ne': 'hOI!'}}),
			(operator.ge, '$gte', 27, {'field_name': {'$gte': 27}}),
			(operator.gt, '$gt', 27, {'field_name': {'$gt': 27}}),
		]
	
	singletons = [
			(operator.neg, '$exists', {'field_name': {'$exists': 0}}),
			(operator.pos, '$exists', {'field_name': {'$exists': 1}}),
			(Queryable.of_type, '$type', {'field_name': {'$type': 'string'}}),
		]
	
	advanced = [
			(Queryable.any, '$in', [1, 2, 3], {'field_name': {'$in': [1, 2, 3]}}),
			(Queryable.none, '$nin', [1, 2, 3], {'field_name': {'$nin': [1, 2, 3]}}),
			(Queryable.all, '$all', [1, 2, 3], {'field_name': {'$all': [1, 2, 3]}}),
			(Queryable.match, '$elemMatch', {'name': "Bob"}, {'field_name': {'$elemMatch': {'name': 'Bob'}}}),
			(Queryable.size, '$size', 42, {'field_name': {'$size': 42}}),
			(Queryable.of_type, '$type', "double", {'field_name': {'$type': 'double'}}),
		]
	
	def do_operator(self, operator, query, value, result):
		op = operator(mock_queryable, value)
		assert isinstance(op, Op)
		assert op.operation == query[1:]
		assert op.as_query == result
		
		if __debug__:
			a = MockQueryable()
			a.__disallowed_operators__ = {query}
			
			try:
				operator(a, value)
			except NotImplementedError as e:
				assert query in str(e)
	
	def do_singleton(self, operator, query, result):
		op = operator(mock_queryable)
		assert isinstance(op, Op)
		assert op.operation == query[1:]
		assert op.as_query == result
	
	# This hides the names of the tests.  Ugh.
	#def test_generated_operation_tests(self):
	#	for expectation in self.expectations:
	#		yield (self.do, ) + expectation
	
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
	def test_operator_all(self): self.do_operator(*self.advanced[2])
	def test_operator_match(self): self.do_operator(*self.advanced[3])
	def test_operator_size(self): self.do_operator(*self.advanced[4])
	def test_operator_type(self): self.do_operator(*self.advanced[5])
	def test_operator_type_assumed(self): self.do_singleton(*self.singletons[2])
