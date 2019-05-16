"""Parameterized support akin to Django's ORM or MongoEngine."""

from collections import namedtuple

from ...package.loader import traverse
from .. import Field, Document
from ..util import odict
from ..query import Q
from ..core.types import Any, Callable, Iterable, Mapping, OperationMap, Optional, Type, Union, namedtuple


def _deferred_method(name:str, _named:Optional[Iterable[str]]=None, **kw) -> Callable:
	def _deferred_method_inner(self, other:Iterable):
		if not _named:
			return getattr(self, name)(other, **kw)
		
		values = iter(other)
		
		for i in _named:
			kw[i] = next(values)
		
		return getattr(self, name)(**kw)
	
	return _deferred_method_inner


def _operator_choice(conversion:Callable, lookup:Mapping, **kw):
	def _operator_choice_inner(self, other):
		return lookup[conversion(other)](self, **kw)
	
	return _operator_choice_inner


class OperationalCandidate(namedtuple('OperationalCandidate', ('prefix', 'suffix', 'field', 'value'))):
	"""A reference to a field within a document, with optional prefix and suffix, and associated value."""
	
	prefix:Optional[Callable]  # A mapped prefix, if present.
	suffix:Optional[Callable]  # A mapped suffix, if present.
	field:Q  # The Document attribute (or sub-attribute thereof) that is a querying interface to the field.
	value:Any  # The provided value, after transformation by the field's transformer.


def _process_arguments(Document:Type[Document], prefixes:OperationMap, suffixes:OperationMap, arguments:Mapping,
		passthrough:Optional[set]=None) -> Iterable[OperationalCandidate]:
	"""Transform collected keyword arguments into a resolved set of fields with optional prefixes and suffixes."""
	
	for name, value in arguments.items():
		prefix, _, nname = name.partition('__')  # Isolate the first element as a prefix.
		if prefix in prefixes: name = nname  # Only consume if a valid, known prefix.
		
		nname, _, suffix = name.rpartition('__')  # Isoltae the last element as a suffix.
		if suffix in suffixes: name = nname  # Only consume if a valid, known suffix.
		
		q = traverse(Document, name, separator='__')  # Find the target field.
		
		if passthrough and not passthrough & {prefix, suffix}:  # Typecast the value to MongoDB-safe as needed.
			value = q._field.transformer.foreign(value, (q._field, Document))  # pylint:disable=protected-access
		
		yield OperationalCandidate(
				prefixes.get(prefix or None, None),
				suffixes.get(suffix or None, None),
				q,
				value
			)


def _current_date(value:Optional[str]) -> Union[Mapping[str, str], bool]:
	if value in ('ts', 'timestamp'):
		return {'$type': 'timestamp'}
	
	return True


def _bit(op: str) -> Callable[[int], Mapping]:
	def bitwiseUpdate(value):
		return odict({op: int(value)})
	
	return bitwiseUpdate
