# encoding: utf-8

"""Parameterized support akin to Django's ORM or MongoEngine."""

from __future__ import unicode_literals

from marrow.package.loader import traverse


def _deferred_method(name, _named=None, **kw):
	def _deferred_method_inner(self, other):
		if _named:
			if isinstance(_named, tuple):
				assert len(_named) == len(other), "Incorrect number of arguments."
				values = iter(other)
				
				for i in _named:
					kw[i] = next(values)
			
			else:
				kw[_named] = other
			
			return getattr(self, name)(**kw)
		
		return getattr(self, name)(other, **kw)
	
	return _deferred_method_inner


def _operator_choice(conversion, lookup, **kw):
	def _operator_choice_inner(self, other):
		return lookup[conversion(other)](self, **kw)
	
	return _operator_choice_inner


def _process_arguments(Document, prefixes, suffixes, arguments):
	for name, value in arguments.items():
		prefix, _, nname = name.partition('__')
		if prefix in prefixes:
			name = nname
		
		nname, _, suffix = name.rpartition('__')
		if suffix in suffixes:
			name = nname
		
		field = traverse(Document, name.replace('__', '.'))  # Find the target field.
		value = field.transformer.foreign(value, (field, Document))  # Typecast the value to MongoDB-safe as needed.
		
		yield prefixes.get(prefix or None, None), suffixes.get(suffix, None), field, value
