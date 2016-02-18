# encoding: utf-8

from copy import deepcopy
from itertools import chain

from marrow.schema import Container, Attribute

SENTINEL = object()


class Ops(Container):
	operations = Attribute(default=dict)
	
	def __repr__(self):
		return "Ops({})".format(repr(self.as_query))
	
	@property
	def as_query(self):
		return self.operations
	
	def __and__(self, other):
		operations = deepcopy(self.operations)
		
		if isinstance(other, Op):
			other = Ops(operations=other.as_query)
		
		for k, v in getattr(other, 'operations', {}).items():
			if k not in operations:
				operations[k] = v
			else:
				if not isinstance(operations[k], dict):
					operations[k] = {'$eq': operations[k]}
				
				if not isinstance(v, dict):
					v = {'$eq': v}
				
				operations[k].update(v)
		
		return Ops(operations=operations)
	
	def __or__(self, other):
		operations = deepcopy(self.operations)
		
		if isinstance(other, Op):
			other = Ops(operations=other.as_query)
		
		if len(operations) == 1 and '$or' in operations:
			# Update existing $or.
			operations['$or'].append(other)
			return Ops(operations=operations)
		
		return Ops(operations={'$or': [operations, other]})


class Op(Container):
	field = Attribute(default=None)
	operation = Attribute(default=None)
	value = Attribute(default=SENTINEL)
	
	def __repr__(self):
		return "Op({})".format(repr(self.as_query))
	
	def clone(self, **kw):
		arguments = dict(field=self.field, operation=self.operation, value=self.value)
		arguments.update(kw)
		return self.__class__(**arguments)
	
	# Logical Query Selectors
	# https://docs.mongodb.org/manual/reference/operator/query/#logical
	
	def __or__(self, other):
		return Op(None, 'or', [self, other])
	
	def __and__(self, other):
		#if isinstance(other, Ops):
		#	return Ops(dict(other.operations))
		
		if getattr(other, 'field', None) is None or self.field is None:
			return Op(None, 'and', [self, other])
		
		return Ops(dict(chain(self.as_query.items(), other.as_query.items())))
	
	def __invert__(self): # not
		return Op(None, '$not', self)
	
	@property
	def as_query(self):
		value = getattr(self.value, 'as_query', self.value)
		if value is SENTINEL:
			value = None
		
		if isinstance(value, list):
			value = [getattr(i, 'as_query', i) for i in value]
		
		if not self.operation or self.operation == 'eq':
			if not self.field:
				return value
			
			if self.value is SENTINEL:
				return {str(self.field): {'$exists': 1}}
			
			return {str(self.field): value}
		
		if not self.field:
			return {'$' + self.operation: value}
		
		return {str(self.field): {'$' + self.operation: value}}
