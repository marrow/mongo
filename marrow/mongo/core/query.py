# encoding: utf-8

"""MongoDB filter, projection, and update operation helpers.

These encapsulate the functionality of creating combinable mappings 
"""

from .util import py2, deepcopy, str, odict, chain, Mapping, MutableMapping, Container, Attribute, SENTINEL


class Ops(Container):
	operations = Attribute(default=None)
	
	def __init__(self, *args, **kw):
		super(Ops, self).__init__(*args, **kw)
		
		if self.operations is None:
			self.operations = odict()
	
	def __repr__(self):
		return "Ops({})".format(repr(list(self)))
	
	@property
	def as_query(self):
		return self.operations
	
	# Binary Operator Protocols
	
	def __and__(self, other):
		operations = deepcopy(self.operations)
		
		if isinstance(other, Op):
			other = Ops(operations=other.as_query)
		
		for k, v in getattr(other, 'operations', []).items():
			if k not in operations:
				operations[k] = v
			else:
				if not isinstance(operations[k], Mapping):
					operations[k] = odict((('$eq', operations[k]), ))
				
				if not isinstance(v, Mapping):
					v = odict((('$eq', v), ))
				
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
	
	# Mapping Protocol
	
	def __getitem__(self, name):
		return self.operations[name]
	
	def __setitem__(self, name, value):
		self.operations[name] = value
	
	def __delitem__(self, name):
		del self.operations[name]
	
	def __iter__(self):
		return iter(self.operations.items())
	
	def __len__(self):
		return len(self.operations)
	
	if py2:
		def keys(self):
			return self.operations.iterkeys()
		
		def items(self):
			return self.operations.iteritems()
		
		def values(self):
			return self.operations.itervalues()
	
	else:
		def keys(self):
			return self.operations.keys()
		
		def items(self):
			return self.operations.items()
		
		def values(self):
			return self.operations.values()
	
	def __contains__(self, key):
		return key in self.operations
	
	def __eq__(self, other):
		return self.operations == other
	
	def __ne__(self, other):
		return self.operations != other
	
	def get(self, key, default=None):
		return self.operations.get(key, default)
	
	def clear(self):
		self.operations.clear()
	
	def pop(self, name, default=SENTINEL):
		if default is SENTINEL:
			return self.operations.pop(name)
		
		return self.operations.pop(name, default)
	
	def popitem(self):
		return self.operations.popitem()
	
	def update(self, *args, **kw):
		self.operations.update(*args, **kw)
	
	def setdefault(self, key, value=None):
		return self.operations.setdefault(key, value)


MutableMapping.register(Ops)  # Metaclass conflict if we subclass.


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
		if getattr(other, 'field', None) is None or self.field is None:
			return Op(None, 'and', [self, other])
		
		return Ops(odict(chain(self.as_query.items(), other.as_query.items())))
	
	def __invert__(self): # not
		return Op(None, 'not', self)
	
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
			return {'$' + str(self.operation): value}
		
		return {str(self.field): {'$' + str(self.operation): value}}
