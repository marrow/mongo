# encoding: utf-8

from __future__ import unicode_literals

import operator

import pytest

from marrow.mongo import Filter
from marrow.schema.compat import odict, py3


@pytest.fixture
def empty_ops(request):
	return Filter()


@pytest.fixture
def single_ops(request):
	return Filter({'roll': 27})


def test_ops_iteration(single_ops):
	assert list(iter(single_ops)) == ['roll']


class TestOpsMapping(object):
	def test_getitem(self, empty_ops, single_ops):
		with pytest.raises(KeyError):
			empty_ops['roll']
		
		assert single_ops['roll'] == 27
	
	def test_setitem(self, empty_ops):
		assert repr(empty_ops) == "Filter([])"
		empty_ops['meaning'] = 42
		
		if py3:
			assert repr(empty_ops) == "Filter([('meaning', 42)])"
		else:
			assert repr(empty_ops) == "Filter([(u'meaning', 42)])"
	
	def test_delitem(self, empty_ops, single_ops):
		with pytest.raises(KeyError):
			del empty_ops['roll']
		
		if py3:
			assert repr(single_ops) == "Filter([('roll', 27)])"
		else:
			assert repr(single_ops) == "Filter([(u'roll', 27)])"
		
		del single_ops['roll']
		assert repr(single_ops) == "Filter([])"
	
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
		
		if py3:
			assert repr(empty_ops) == "Filter([('name', 'Bob Dole')])"
		else:
			assert repr(empty_ops) == "Filter([('name', u'Bob Dole')])"
		
		assert len(single_ops.operations) == 1
		
		if py3:
			assert repr(single_ops) == "Filter([('roll', 27)])"
		else:
			assert repr(single_ops) == "Filter([(u'roll', 27)])"
		
		single_ops.update([('name', "Bob Dole")])
		assert len(single_ops.operations) == 2
		
		if py3:
			assert repr(single_ops) in ("Filter([('roll', 27), ('name', 'Bob Dole')])", "Filter([('name', 'Bob Dole'), ('roll', 27)])")
		else:
			assert repr(single_ops) in ("Filter([(u'roll', 27), (u'name', u'Bob Dole')])", "Filter([(u'name', u'Bob Dole'), (u'roll', 27)])")
	
	def test_setdefault(self, empty_ops):
		assert len(empty_ops.operations) == 0
		empty_ops.setdefault('fnord', 42)
		assert len(empty_ops.operations) == 1
		assert empty_ops.operations['fnord'] == 42
		empty_ops.setdefault('fnord', 27)
		assert len(empty_ops.operations) == 1
		assert empty_ops.operations['fnord'] == 42
	
	def test_ops_shallow_copy(self, single_ops):
		assert single_ops.operations == single_ops.copy().operations


class TestOperationsCombination(object):
	def test_operations_and_clean_merge(self):
		comb = Filter({'roll': 27}) & Filter({'foo': 42})
		assert comb.as_query == {'roll': 27, 'foo': 42}
	
	def test_operations_and_operator_overlap(self):
		comb = Filter({'roll': {'$gte': 27}}) & Filter({'roll': {'$lte': 42}})
		assert comb.as_query == {'roll': {'$gte': 27, '$lte': 42}}
	
	def test_paradoxical_condition(self):
		comb = Filter({'roll': 27}) & Filter({'roll': {'$lte': 42}})
		assert comb.as_query == {'roll': {'$eq': 27, '$lte': 42}}
		
		comb = Filter({'roll': {'$gte': 27}}) & Filter({'roll': 42})
		assert list(comb.as_query['roll'].items()) in ([('$gte', 27), ('$eq', 42)], [('$eq', 42), ('$gte', 27)])
	
	def test_operations_or_clean_merge(self):
		comb = Filter({'roll': 27}) | Filter({'foo': 42})
		assert comb.as_query == {'$or': [{'roll': 27}, {'foo': 42}]}
		
		comb = comb | Filter({'bar': 'baz'})
		assert comb.as_query == {'$or': [{'roll': 27}, {'foo': 42}, {'bar': 'baz'}]}
	
	def test_operations_hard_and(self):
		comb = Filter({'$and': [{'a': 1}, {'b': 2}]}) & Filter({'$and': [{'c': 3}]})
		assert comb.as_query == {'$and': [{'a': 1}, {'b': 2}, {'c': 3}]}
	
	def test_operations_soft_and(self):
		comb = Filter({'$and': [{'a': 1}, {'b': 2}]}) & Filter({'c': 3})
		assert comb.as_query == {'$and': [{'a': 1}, {'b': 2}], 'c': 3}
